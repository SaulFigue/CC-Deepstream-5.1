/*
 * Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
 *
 * NVIDIA Corporation and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA Corporation is strictly prohibited.
 *
 */

/**
 * @file
 * <b>NVIDIA DeepStream: Message Schema Generation Library Interface</b>
 *
 * @b Description: This file specifies the NVIDIA DeepStream message schema generation
 * library interface.
 */

#ifndef NVMSGCONV_H_
#define NVMSGCONV_H_


#include "nvdsmeta_schema.h"
#include <glib.h>

#ifdef __cplusplus
extern "C"
{
#endif

// ================= Saul ==================

typedef struct NvDsEventMsgMeta {
  /** Holds the event's type. */
  NvDsEventType type;
  /** Holds the object's type. */
  NvDsObjectType objType;
  /** Holds the object's bounding box. */
  NvDsRect bbox;
  /** Holds the object's geolocation. */
  NvDsGeoLocation location;
  /** Holds the object's coordinates. */
  NvDsCoordinate coordinate;
  /** Holds the object's signature. */
  NvDsObjectSignature objSignature;
  /** Holds the object's class ID. */
  gint objClassId;
  /** Holds the ID of the sensor that generated the event. */
  gint sensorId;
  /** Holds the ID of the analytics module that generated the event. */
  gint moduleId;
  /** Holds the ID of the place related to the object. */
  gint placeId;
  /** Holds the ID of the component (plugin) that generated this event. */
  gint componentId;
  /** Holds the video frame ID of this event. */
  gint frameId;
  /** Holds the confidence level of the inference. */
  gdouble confidence;
  /** Holds the object's tracking ID. */
  gint trackingId;
  /** Holds a pointer to the generated event's timestamp. */
  gchar *ts;
  /** Holds a pointer to the detected or inferred object's ID. */
  gchar *objectId;

  /** Holds a pointer to a string containing the sensor's identity. */
  gchar *sensorStr;
  /** Holds a pointer to a string containing other attributes associated with
   the object. */
  gchar *otherAttrs;
  /** Holds a pointer to the name of the video file. */
  gchar *videoPath;
  /** Holds a pointer to event message meta data. This can be used to hold
   data that can't be accommodated in the existing fields, or an associated
   object (representing a vehicle, person, face, etc.). */
  gpointer extMsg;
  /** Holds the number of line-crossings captured in the current frame */
  gint lcNum;
  /** Holds the stream ID */
  gint streamId;
  /** Holds the size of the custom object at @a extMsg. */
  guint extMsgSize;
  
  //---------------------- CUSTOM CODE --------------------//
  
  // Flujo Meta
  gint fcamera_id;
  gint fframe_init;
  gint fframe_fin;
  gint ffreq;
  gint fobj_type;
  gint lc_names_size;
  gint cross_count;
  
  // Aforo Meta
  // OLD
  gint aanalytic;
  gint aperson_max_count[10];
  gint aperson_min_count[10];
  gint acar_max_count[10];
  gint acar_min_count[10];
  gint aperson_roi_id[10];
  gint acar_roi_id[10];
  ////////

  
  // AFORO
  gint acamera_id;
  gint aframe_init;
  gint aframe_fin;
  gint afreq;
  gint aavg_person_count[10];
  gint aavg_car_count[10];
  gint aobj_type;
  gint aperson_array;
  gint acar_array;

  // Permanencia OLD
  gint person_ids[1000];
  gint car_ids[1000];
  gint person_size;
  gint car_size;
  gint permanencia_person;
  gint permanencia_car;

  // PERMANENCIA
  gint permanencia_ids[1000];
  gint permanencia_size;
  gint permanencia_is_active;
  
  // Atributos Meta
  gint sgie_names_size;
  gint count_males[10];
  gint count_females[10];
  

  gint m_1_18[10];
  gint m_19_50[10];
  gint m_gt_50[10];

  gint f_1_18[10];
  gint f_19_50[10];
  gint f_gt_50[10];
  //-----------------------------------------------------------------------------------------//
  //
} NvDsEventMsgMeta;

typedef struct _NvDsEvent {
  /** Holds the type of event. */
  NvDsEventType eventType;
  /** Holds a pointer to event metadata. */
  NvDsEventMsgMeta *metadata;
} NvDsEvent;

// ========================================================


/**
 * @ref NvDsMsg2pCtx is structure for library context.
 */
typedef struct NvDsMsg2pCtx {
  /** type of payload to be generated. */
  NvDsPayloadType payloadType;

  /** private to component. Don't change this field. */
  gpointer privData;
} NvDsMsg2pCtx;

/**
 * This function initializes the library with user defined options mentioned
 * in the file and returns the handle to the context.
 * Static fields which should be part of message payload can be added to
 * file instead of frame metadata.
 *
 * @param[in] file name of file to read static properties from.
 * @param[in] type type of payload to be generated.
 *
 * @return pointer to library context created. This context should be used in
 * other functions of library and should be freed with
 * @ref nvds_msg2p_ctx_destroy
 */
NvDsMsg2pCtx* nvds_msg2p_ctx_create (const gchar *file, NvDsPayloadType type);

/**
 * Release the resources allocated during context creation.
 *
 * @param[in] ctx pointer to library context.
 */
void nvds_msg2p_ctx_destroy (NvDsMsg2pCtx *ctx);

/**
 * This function will parse the @ref NvDsEventMsgMeta and will generate message
 * payload. Payload will be combination of static values read from
 * configuration file and dynamic values received in meta.
 * Payload will be generated based on the @ref NvDsPayloadType type provided
 * in context creation (e.g. Deepstream, Custom etc.).
 *
 * @param[in] ctx pointer to library context.
 * @param[in] events pointer to array of event objects.
 * @param[in] size number of objects in array.
 *
 * @return pointer to @ref NvDsPayload generated or NULL in case of error.
 * This payload should be freed with @ref nvds_msg2p_release
 */
NvDsPayload*
nvds_msg2p_generate (NvDsMsg2pCtx *ctx, NvDsEvent *events, guint size);

/**
 * This function will parse the @ref NvDsEventMsgMeta and will generate multiple
 * message payloads. Payloads will be combination of static values read from
 * configuration file and dynamic values received in meta.
 * Payloads will be generated based on the @ref NvDsPayloadType type provided
 * in context creation (e.g. Deepstream, Custom etc.).
 *
 * @param[in] ctx pointer to library context.
 * @param[in] events pointer to array of event objects.
 * @param[in] size number of objects in array.
 * @param[out] payloadCount number of payloads being returned by the function.
 *
 * @return pointer to @ref array of NvDsPayload pointers generated or NULL in
 * case of error. The number of payloads in the array is returned through
 * payloadCount. This pointer should be freed by calling g_free() and the
 * individual payloads should be freed with @ref nvds_msg2p_release
 */
NvDsPayload**
nvds_msg2p_generate_multiple (NvDsMsg2pCtx *ctx, NvDsEvent *events, guint size, guint *payloadCount);

/**
 * This function should be called to release memory allocated for payload.
 *
 * @param[in] ctx pointer to library context.
 * @param[in] payload pointer to object that needs to be released.
 */
void nvds_msg2p_release (NvDsMsg2pCtx *ctx, NvDsPayload *payload);

#ifdef __cplusplus
}
#endif
#endif /* NVMSGCONV_H_ */
