// tvm target: c -keys=cortex-m4,cpu -device=cortex-m4
#define TVM_EXPORTS
#include "tvm/runtime/c_runtime_api.h"
#include "tvm/runtime/c_backend_api.h"
#include <math.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_add(float* p0, float* T_add, uint8_t* global_const_workspace_2_var, uint8_t* global_workspace_3_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add(float* p0, float* T_add, uint8_t* global_const_workspace_8_var, uint8_t* global_workspace_9_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_1(float* p0, float* T_add, uint8_t* global_const_workspace_10_var, uint8_t* global_workspace_11_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add(float* p0, float* T_add, uint8_t* global_const_workspace_4_var, uint8_t* global_workspace_5_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add_1(float* p0, float* T_add, uint8_t* global_const_workspace_6_var, uint8_t* global_workspace_7_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_softmax(float* p0, float* T_softmax_norm, uint8_t* global_const_workspace_12_var, uint8_t* global_workspace_13_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default___tvm_main__(float* input_1_buffer_var, float* output_buffer_var, uint8_t* global_const_workspace_0_var, uint8_t* global_workspace_1_var);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL float expf(float);
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_add(float* p0, float* T_add, uint8_t* global_const_workspace_2_var, uint8_t* global_workspace_3_var) {
  void* fused_constant_let = (&(global_const_workspace_2_var[39680]));
  for (int32_t ax1_outer = 0; ax1_outer < 8; ++ax1_outer) {
    for (int32_t ax1_inner = 0; ax1_inner < 16; ++ax1_inner) {
      if (((ax1_outer * 16) + ax1_inner) < 115) {
        int32_t cse_var_1 = ((ax1_outer * 16) + ax1_inner);
        T_add[cse_var_1] = (p0[cse_var_1] + ((float*)fused_constant_let)[cse_var_1]);
      }
    }
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add(float* p0, float* T_add, uint8_t* global_const_workspace_8_var, uint8_t* global_workspace_9_var) {
  void* fused_nn_contrib_dense_pack_constant_2_let = (&(global_const_workspace_8_var[41232]));
  void* fused_constant_3_let = (&(global_const_workspace_8_var[37632]));
  for (int32_t ax1_outer_ax0_outer_fused = 0; ax1_outer_ax0_outer_fused < 2; ++ax1_outer_ax0_outer_fused) {
    void* compute_global_let = (&(global_workspace_9_var[192]));
    for (int32_t x_c_init = 0; x_c_init < 8; ++x_c_init) {
      ((float*)compute_global_let)[x_c_init] = 0.000000e+00f;
    }
    for (int32_t k_outer = 0; k_outer < 32; ++k_outer) {
      for (int32_t x_c = 0; x_c < 8; ++x_c) {
        ((float*)compute_global_let)[x_c] = (((float*)compute_global_let)[x_c] + (p0[k_outer] * ((float*)fused_constant_3_let)[(((ax1_outer_ax0_outer_fused * 256) + (k_outer * 8)) + x_c)]));
      }
    }
    for (int32_t ax1_inner_inner = 0; ax1_inner_inner < 8; ++ax1_inner_inner) {
      int32_t cse_var_1 = ((ax1_outer_ax0_outer_fused * 8) + ax1_inner_inner);
      T_add[cse_var_1] = (((float*)compute_global_let)[ax1_inner_inner] + ((float*)fused_nn_contrib_dense_pack_constant_2_let)[cse_var_1]);
    }
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_1(float* p0, float* T_add, uint8_t* global_const_workspace_10_var, uint8_t* global_workspace_11_var) {
  void* fused_nn_contrib_dense_pack_constant_3_let = (&(global_const_workspace_10_var[41296]));
  void* fused_constant_4_let = (&(global_const_workspace_10_var[40144]));
  void* compute_global_let = (&(global_workspace_11_var[32]));
  for (int32_t x_c_init = 0; x_c_init < 5; ++x_c_init) {
    ((float*)compute_global_let)[x_c_init] = 0.000000e+00f;
  }
  for (int32_t k_outer = 0; k_outer < 16; ++k_outer) {
    for (int32_t x_c = 0; x_c < 5; ++x_c) {
      ((float*)compute_global_let)[x_c] = (((float*)compute_global_let)[x_c] + (p0[k_outer] * ((float*)fused_constant_4_let)[((k_outer * 5) + x_c)]));
    }
  }
  for (int32_t ax1_inner_inner = 0; ax1_inner_inner < 5; ++ax1_inner_inner) {
    T_add[ax1_inner_inner] = (((float*)compute_global_let)[ax1_inner_inner] + ((float*)fused_nn_contrib_dense_pack_constant_3_let)[ax1_inner_inner]);
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add(float* p0, float* T_add, uint8_t* global_const_workspace_4_var, uint8_t* global_workspace_5_var) {
  void* fused_nn_contrib_dense_pack_add_nn_relu_constant_let = (&(global_const_workspace_4_var[40720]));
  void* fused_nn_contrib_dense_pack_constant_let = (&(global_const_workspace_4_var[40464]));
  void* fused_constant_1_let = (&(global_const_workspace_4_var[0]));
  for (int32_t ax1_outer_ax0_outer_fused = 0; ax1_outer_ax0_outer_fused < 4; ++ax1_outer_ax0_outer_fused) {
    void* compute_let = (&(global_workspace_5_var[720]));
    void* compute_global_let = (&(global_workspace_5_var[784]));
    for (int32_t y_inner_outer_x_inner_outer_fused = 0; y_inner_outer_x_inner_outer_fused < 2; ++y_inner_outer_x_inner_outer_fused) {
      for (int32_t x_c_init = 0; x_c_init < 8; ++x_c_init) {
        ((float*)compute_global_let)[x_c_init] = 0.000000e+00f;
      }
      for (int32_t k_outer = 0; k_outer < 115; ++k_outer) {
        for (int32_t x_c = 0; x_c < 8; ++x_c) {
          ((float*)compute_global_let)[x_c] = (((float*)compute_global_let)[x_c] + (p0[k_outer] * ((float*)fused_constant_1_let)[((((ax1_outer_ax0_outer_fused * 1840) + (y_inner_outer_x_inner_outer_fused * 920)) + (k_outer * 8)) + x_c)]));
        }
      }
      for (int32_t x_inner_inner = 0; x_inner_inner < 8; ++x_inner_inner) {
        ((float*)compute_let)[((y_inner_outer_x_inner_outer_fused * 8) + x_inner_inner)] = ((float*)compute_global_let)[x_inner_inner];
      }
    }
    for (int32_t ax1_inner_outer = 0; ax1_inner_outer < 2; ++ax1_inner_outer) {
      for (int32_t ax1_inner_inner = 0; ax1_inner_inner < 8; ++ax1_inner_inner) {
        int32_t cse_var_2 = (ax1_inner_outer * 8);
        int32_t cse_var_1 = (((ax1_outer_ax0_outer_fused * 16) + cse_var_2) + ax1_inner_inner);
        float v_ = ((float*)compute_let)[(cse_var_2 + ax1_inner_inner)] + ((float*)fused_nn_contrib_dense_pack_constant_let)[cse_var_1];
        T_add[cse_var_1] = (((v_) > (0.000000e+00f) ? (v_) : (0.000000e+00f)) + ((float*)fused_nn_contrib_dense_pack_add_nn_relu_constant_let)[cse_var_1]);
      }
    }
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add_1(float* p0, float* T_add, uint8_t* global_const_workspace_6_var, uint8_t* global_workspace_7_var) {
  void* fused_nn_contrib_dense_pack_add_nn_relu_constant_1_let = (&(global_const_workspace_6_var[41104]));
  void* fused_nn_contrib_dense_pack_constant_1_let = (&(global_const_workspace_6_var[40976]));
  void* fused_constant_2_let = (&(global_const_workspace_6_var[29440]));
  for (int32_t ax1_outer_ax0_outer_fused = 0; ax1_outer_ax0_outer_fused < 4; ++ax1_outer_ax0_outer_fused) {
    void* compute_global_let = (&(global_workspace_7_var[128]));
    for (int32_t x_c_init = 0; x_c_init < 8; ++x_c_init) {
      ((float*)compute_global_let)[x_c_init] = 0.000000e+00f;
    }
    for (int32_t k_outer = 0; k_outer < 64; ++k_outer) {
      for (int32_t x_c = 0; x_c < 8; ++x_c) {
        ((float*)compute_global_let)[x_c] = (((float*)compute_global_let)[x_c] + (p0[k_outer] * ((float*)fused_constant_2_let)[(((ax1_outer_ax0_outer_fused * 512) + (k_outer * 8)) + x_c)]));
      }
    }
    for (int32_t ax1_inner_inner = 0; ax1_inner_inner < 8; ++ax1_inner_inner) {
      int32_t cse_var_1 = ((ax1_outer_ax0_outer_fused * 8) + ax1_inner_inner);
      float v_ = ((float*)compute_global_let)[ax1_inner_inner] + ((float*)fused_nn_contrib_dense_pack_constant_1_let)[cse_var_1];
      T_add[cse_var_1] = (((v_) > (0.000000e+00f) ? (v_) : (0.000000e+00f)) + ((float*)fused_nn_contrib_dense_pack_add_nn_relu_constant_1_let)[cse_var_1]);
    }
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_fused_nn_softmax(float* p0, float* T_softmax_norm, uint8_t* global_const_workspace_12_var, uint8_t* global_workspace_13_var) {
  void* T_softmax_maxelem_let = (&(global_workspace_13_var[64]));
  void* T_softmax_exp_let = (&(global_workspace_13_var[32]));
  void* T_softmax_expsum_let = (&(global_workspace_13_var[0]));
  ((float*)T_softmax_maxelem_let)[0] = -3.402823e+38f;
  for (int32_t k = 0; k < 5; ++k) {
    float v_ = ((float*)T_softmax_maxelem_let)[0];
    float v__1 = p0[k];
    ((float*)T_softmax_maxelem_let)[0] = ((v_) > (v__1) ? (v_) : (v__1));
  }
  for (int32_t i1 = 0; i1 < 5; ++i1) {
    ((float*)T_softmax_exp_let)[i1] = expf((p0[i1] - ((float*)T_softmax_maxelem_let)[0]));
  }
  ((float*)T_softmax_expsum_let)[0] = 0.000000e+00f;
  for (int32_t k_1 = 0; k_1 < 5; ++k_1) {
    ((float*)T_softmax_expsum_let)[0] = (((float*)T_softmax_expsum_let)[0] + ((float*)T_softmax_exp_let)[k_1]);
  }
  for (int32_t i1_1 = 0; i1_1 < 5; ++i1_1) {
    T_softmax_norm[i1_1] = (((float*)T_softmax_exp_let)[i1_1] / ((float*)T_softmax_expsum_let)[0]);
  }
  return 0;
}

#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default___tvm_main__(float* input_1_buffer_var, float* output_buffer_var, uint8_t* global_const_workspace_0_var, uint8_t* global_workspace_1_var) {
  void* sid_1_let = (&(global_workspace_1_var[0]));
  void* sid_2_let = (&(global_workspace_1_var[464]));
  void* sid_3_let = (&(global_workspace_1_var[0]));
  void* sid_4_let = (&(global_workspace_1_var[128]));
  void* sid_5_let = (&(global_workspace_1_var[0]));
  if (tvmgen_default_fused_add(input_1_buffer_var, sid_1_let, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  if (tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add(sid_1_let, sid_2_let, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  if (tvmgen_default_fused_nn_contrib_dense_pack_add_nn_relu_add_1(sid_2_let, sid_3_let, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  if (tvmgen_default_fused_nn_contrib_dense_pack_add(sid_3_let, sid_4_let, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  if (tvmgen_default_fused_nn_contrib_dense_pack_add_1(sid_4_let, sid_5_let, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  if (tvmgen_default_fused_nn_softmax(sid_5_let, output_buffer_var, global_const_workspace_0_var, global_workspace_1_var) != 0 ) return -1;
  return 0;
}

