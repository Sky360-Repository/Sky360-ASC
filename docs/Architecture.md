# s360-asc-node Architecture
Sky360 Project - ASC Node Specification

## 1. Overview

`s360-asc-node` is the **primary vision-processing node** in the Sky360 system.

Its purpose is to:
- Control and acquire frames from **All-Sky Cameras** (QHY, ZWO, USB)
- Run the **Image Signal Processing (ISP)** pipeline
- Execute the **Computer Vision (CV)** pipeline (GMM, ViBe, DoG, MHI, optical flow, blob detection)
- Produce **event lists** (motion, blobs, POIs, tracks)
- Run **TinyML inference** on the NPU for semantic classification
- Publish structured protobuf messages over **eCAL**
- Provide camera status, logs, and CV outputs to other nodes (PTF, CORE, NAS)

## 2. High-Level Architecture

```
s360-asc-node
 +-- orchestrator/
 |     +-- main orchestrator loop
 |     +-- module lifecycle mgmt
 |     +-- eCAL publishers/subscribers
 |     +-- frame routing + event routing
 |
 +-- camera/
 |     +-- QHY/ZWO/USB camera controller
 |     +-- RAW frame acquisition
 |     +-- pb.sky.AllSkyCameraData publisher
 |
 +-- isp/
 |     +-- RAW - grayscale conversion
 |     +-- RGB 2x2 reconstruction
 |     +-- compression (lz4/zlib)
 |     +-- sensor metadata extraction
 |
 +-- cv/
 |     +-- GMM / ViBe background subtraction
 |     +-- 3-frame differencing (RGB + gradient)
 |     +-- DoG + Harris + SIFT/ORB POI detection
 |     +-- MHI temporal scoring
 |     +-- blob detection + contour analysis
 |     +-- event list generator
 |     +-- pb.sky.AscEventList publisher
 |
 +-- tinyml/
       +-- NPU inference (classification)
       +-- event semantic labeling
       +-- pb.sky.AscSemanticEvent publisher
```


## 3. Component Responsibilities

### **Orchestrator**
- Starts/stops modules
- Routes frames from camera - ISP - CV - TinyML
- Publishes heartbeat/status
- Manages eCAL publishers/subscribers
- Ensures deterministic processing order
- Handles backpressure (frame dropping, queue limits)

### **Camera Module**
- Interfaces with QHY, ZWO, USB cameras
- Acquires RAW frames (RAW8/RAW12/RAW16)
- Generates JPEG preview and optional H264
- Publishes `pb.sky.AllSkyCameraData`
- Provides sensor metadata (gain, exposure, temperature)

### **ISP Module**
- Converts RAW - grayscale (uint16)
- Reconstructs RGB 2x2 (for fisheye cameras)
- Compresses CV streams (lz4/zlib)
- Normalizes sensor metadata
- Provides clean inputs to CV pipeline

### **CV Pipeline Module**
- Background subtraction (GMM, ViBe)
- Motion detection (3-frame diff, gradient diff)
- POI detection (DoG, Harris, SIFT/ORB)
- Motion History Image (MHI) scoring
- Blob detection + contour extraction
- Event list generation (motion, blob, POI, track)
- Publishes `AscEventList`

### **TinyML Module**
- Runs NPU inference on event ROIs
- Classifies events (aircraft, bird, satellite, unknown)
- Publishes `AscSemanticEvent`
- Provides confidence scores


# 4. Interfaces

Below are the formal interface definitions for **data flow**, **processing stages**, **inputs**, **outputs**, and **eCAL topics**.


## 4.1 DATA FLOW & ARCHITECTURE

| Component | Direction | Data Type | Topic | Description |
|----------|-----------|-----------|--------|-------------|
| Camera Module | Out | `pb.sky.AllSkyCameraData` | `sky360/asc/frame` | RAW frame + JPEG + metadata |
| ISP Module | Internal | Grayscale + RGB2x2 | - | Preprocessed CV streams |
| CV Pipeline | Out | `AscEventList` | `sky360/asc/events` | Motion/blobs/POIs/tracks |
| TinyML Module | Out | `AscSemanticEvent` | `sky360/asc/semantic` | Classified events |
| Orchestrator | Out | `AscStatus` | `sky360/asc/status` | Node health |
| Orchestrator | In | `TimingMessage` | `sky360/timing` | GNSS time alignment |
| Orchestrator | In | `GpsLog` | `sky360/gps` | GNSS positioning (optional) |


## 4.2 PROCESSING STAGES

| Stage | Process | Input | Output | Configurable | Notes |
|-------|---------|--------|---------|--------------|-------|
| Frame Acquisition | RAW capture | Camera | RAW frame | Gain, exposure | Supports QHY, ZWO, USB |
| ISP | RAW - grayscale/RGB2x2 | RAW | CV streams | Compression | Deterministic |
| Background Subtraction | GMM/ViBe | Grayscale | Foreground mask | Learning rate | Supports masks |
| Motion Detection | 3FD + gradient | Grayscale | Motion mask | Thresholds | Fast transient detection |
| POI Detection | DoG/Harris/SIFT | Grayscale | POI list | s values | Multi-scale |
| MHI | Temporal scoring | Motion mask | MHI heatmap | Decay rate | Slow/static motion |
| Blob Detection | Contours | Foreground mask | Blob list | Min area | Morphology |
| Event Generation | Fusion | Blobs + POIs + MHI | Event list | Logic rules | Criterion List |
| TinyML | NPU inference | Event ROIs | Semantic events | Model path | RK3588 NPU |


## 4.3 INPUT FIELDS (Camera - ASC)

### **AllSkyCameraImage Input Fields**

| Field Name | Proto Type | Required | Default | Range/Values | Description |
|------------|------------|----------|---------|--------------|-------------|
| width | uint32 | Yes | - | >0 | Image width |
| height | uint32 | Yes | - | >0 | Image height |
| bit_per_pixel | uint32 | Yes | - | 8/12/16 | RAW bit depth |
| raw_image | bytes | Yes | - | RAW8/RAW12/RAW16 | Lossless RAW frame |
| jpeg_image | bytes | Optional | - | JPEG | Preview |
| full_gray | bytes | Optional | - | compressed uint16 | ISP grayscale |
| rgb_2x2 | bytes | Optional | - | compressed uint16 | ISP RGB2x2 |
| sensor_id | uint32 | Yes | - | 1..N | Camera model |
| source | string | Yes | - | QHY/ZWO/USB | Camera type |
| frame_id | string | Yes | - | ASCII | Frame identifier |
| epoch_time | Timestamp | Yes | - | GNSS time | Sensor timestamp |
| mono_time | Timestamp | Yes | - | Monotonic | Local timestamp |
| temperature | float | Optional | - | °C | Sensor temp |
| gain | float | Optional | - | 0..N | Sensor gain |
| exposure_us | float | Optional | - | µs | Exposure time |


## 4.4 OUTPUT FIELDS (ASC - other nodes)

### **Event List Output (CV Pipeline)**

| Field | Type | Description |
|-------|------|-------------|
| event_id | string | Unique ID |
| x, y | float | Pixel coordinates |
| width, height | float | ROI size |
| score | float | Motion/POI score |
| type | string | motion/blob/poi/track |
| timestamp | Timestamp | Event time |

### **Semantic Event Output (TinyML)**

| Field | Type | Description |
|-------|------|-------------|
| event_id | string | ID from CV pipeline |
| label | string | aircraft/bird/satellite/unknown |
| confidence | float | 0.0–1.0 |
| timestamp | Timestamp | Classification time |

### **Camera Status Output**

| Field | Type | Description |
|-------|------|-------------|
| sensor_id | uint32 | Camera model |
| gain | float | Current gain |
| exposure_us | float | Exposure |
| temperature | float | Sensor temperature |
| fps | float | Measured frame rate |
| is_live | bool | Streaming state |


# 5. eCAL TOPIC DEFINITIONS

| Topic Name | Direction | Message Type | Description |
|------------|-----------|--------------|-------------|
| `sky360/asc/frame` | Out | `pb.sky.AllSkyCameraData` | RAW frame + JPEG + metadata |
| `sky360/asc/status` | Out | `AllSkyCameraStatusData` | Camera status |
| `sky360/asc/logs` | Out | `AllSkyLogs` | Camera logs |
| `sky360/asc/events` | Out | `AscEventList` | CV event list |
| `sky360/asc/semantic` | Out | `AscSemanticEvent` | TinyML classification |
| `sky360/timing` | In | `TimingMessage` | GNSS time alignment |
| `sky360/gps` | In | `GpsLog` | GNSS positioning |

