#!/bin/bash

rm -rf dist/
mkdir dist/

# Build WASM related files.
bazel build --copt="-pthread" --copt="-msimd128" //tensorflow_lite_support/web/tflite_model_runner/cc:tflite_model_runner_wasm
WASM_DIR=../../../../bazel-bin/tensorflow_lite_support/web/tflite_model_runner/cc/tflite_model_runner_wasm/
cp ${WASM_DIR}/tflite_model_runner_cc.js \
   ${WASM_DIR}/tflite_model_runner_cc.wasm \
   ${WASM_DIR}/tflite_model_runner_cc.worker.js \
   dist/

bazel build --copt="-msimd128" //tensorflow_lite_support/web/tflite_model_runner/cc:tflite_model_runner_wasm_st
WASM_DIR=../../../../bazel-bin/tensorflow_lite_support/web/tflite_model_runner/cc/tflite_model_runner_wasm_st/
cp ${WASM_DIR}/tflite_model_runner_cc_st.js \
   ${WASM_DIR}/tflite_model_runner_cc_st.wasm \
   dist/


