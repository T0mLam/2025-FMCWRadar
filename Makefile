.PHONY: all tvm tvm-compile

# Launch the ti tvm container for running custom commands
tvm: 
	docker build -f docker/Dockerfile.tvm -t ti-tvm .
	docker run -it --rm -v $(CURDIR):/workspace ti-tvm

# Shortcut to launch the ti tvm container and compile onnx files to c binaries  
# USAGE: make tvm-compile MODEL_PATH=./your_model_name.onnx OUT_DIR=./model_artifacts
tvm-compile:
	docker build -f docker/Dockerfile.tvm -t ti-tvm .
	docker run -it --rm -v $(CURDIR):/workspace \
		-e MODEL_PATH=$(MODEL_PATH) \
		-e OUT_DIR=$(OUT_DIR) \
		ti-tvm -c "sed -i 's/\r$$//' /workspace/scripts/linux/compile_model.sh && /bin/bash /workspace/scripts/linux/compile_model.sh"