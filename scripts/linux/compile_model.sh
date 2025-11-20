#!/bin/bash
set -e

# Print a nice header with timestamp
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
echo "================================================================================"
echo "Model compile started: $(timestamp)"
echo "================================================================================"

MODEL_PATH=${MODEL_PATH:-"./model.onnx"}
MODEL_NAME=${MODEL_PATH%.*}
OUT_DIR=${OUT_DIR:-"./model"}
OUT_SRC_DIR=$OUT_DIR/src

echo "-> Using model path: $MODEL_PATH"
echo "-> Output directory: $OUT_DIR"

echo "--------------------------------------------------------------------------------"
echo "Section: prepare output"
echo "--------------------------------------------------------------------------------"

mkdir -p "$OUT_SRC_DIR"

echo "-> Created output dir: $OUT_DIR"

echo "--------------------------------------------------------------------------------"
echo "Section: compiler options"
echo "--------------------------------------------------------------------------------"

# Compiler and TVM options 
export TVMC_OPTIONS="--target-c-device=cortex-m4 --runtime=crt --executor=aot \
--executor-aot-interface-api=c --executor-aot-unpacked-api=1 \
--pass-config tir.disable_vectorize=1 --pass-config tir.usmp.algorithm=hill_climb --output-format=a"
export TIARMCLANG_OPTIONS="-Os -mcpu=cortex-m4 -march=armv7e-m -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16"

echo "TVMC options: $TVMC_OPTIONS"
echo "Cross-compiler options: $TIARMCLANG_OPTIONS"

echo "--------------------------------------------------------------------------------"
echo "Section: compile"
echo "--------------------------------------------------------------------------------"

# Run compilation 
echo "> Running: tvmc compile ..."
tvmc compile $TVMC_OPTIONS --verbose --target="c" "$MODEL_PATH" \
    -o "$OUT_DIR/$MODEL_NAME.a" \
    --cross-compiler="tiarmclang" \
    --cross-compiler-options="$TIARMCLANG_OPTIONS"

echo "-> tvmc compile finished"

echo "--------------------------------------------------------------------------------"
echo "Section: package"
echo "--------------------------------------------------------------------------------"

# Move all c files to src/ folder
mv $OUT_DIR/*.c $OUT_SRC_DIR

echo "-> Success - Model compiled and saved to: $OUT_DIR"
echo "================================================================================"
echo "Model compile finished: $(timestamp)"
echo "================================================================================"