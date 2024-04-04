
/*
 * Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

#include <gst/gst.h>
#include <glib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <sys/time.h>
#include <iostream>
#include <unordered_map>
#include <sstream>
#include <cuda_runtime_api.h>
#include "gstnvdsmeta.h"
#include "nvds_analytics_meta.h"
#ifndef PLATFORM_TEGRA
#include "gst-nvmessage.h"
#endif

#define LC_IN "in"
#define LC_OUT "out"

using namespace std;


typedef struct _PairxFrame
{
  gchar **first;
  gint *second;
  gint lcNum;
}PairxFrame;

extern "C" void getLCCount(NvDsFrameMeta *frame_meta, guint32 stream_id, PairxFrame *pares)
{
  stringstream out_string;
  string lc_type = "";
  
  /* Iterate user metadata in frames to search analytics metadata */
  for (NvDsMetaList *l_user = frame_meta->frame_user_meta_list; l_user != NULL; l_user = l_user->next)
  {

    NvDsUserMeta *user_meta = (NvDsUserMeta *) l_user->data;
    if (user_meta->base_meta.meta_type != NVDS_USER_FRAME_META_NVDSANALYTICS){
        continue;
    }

    /* convert to  metadata */
    NvDsAnalyticsFrameMeta *meta = (NvDsAnalyticsFrameMeta *) user_meta->user_meta_data;
    /* Get the labels from nvdsanalytics config file */
    int ii = 0;
    for (std::pair<std::string, uint32_t> status : meta->objLCCurrCnt){     
      // ============================= SAUL ===================================
      //if(status.second != 0){
      pares->first[ii] = g_strdup(status.first.c_str());
      pares->second[ii] = status.second;
      ii++;
    }
    pares->lcNum = ii;
  }
}