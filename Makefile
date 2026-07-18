PYTHON ?= python3
BUILD_DIR ?= build/host
ARTIFACTS ?= artifacts
SSD_SIM_PROFILE ?= synthetic_1g
SSD_SIM_SEED ?= 1
STORAGE_BACKEND ?= simulator
STORAGE_PROFILE ?= synthetic_1g
STORAGE_SEED ?= 1

.PHONY: bootstrap format-check lint build test verify clean ssd-sim-verify storage-verify
bootstrap:
	./tools/bootstrap.sh
format-check:
	$(PYTHON) tools/check_repository.py --format-check
lint:
	$(PYTHON) tools/check_repository.py --lint
build:
	cmake --preset host
	cmake --build --preset host

test: build
	ctest --preset host --output-on-failure
verify:
	./tools/verify.sh --profile ci --clean --emit-manifest $(ARTIFACTS)/build-manifest.json
clean:
	rm -rf build artifacts .pytest_cache **/__pycache__
ssd-sim-verify:
	PYTHONPATH=simulator/ssd/src $(PYTHON) -m pytest simulator/ssd/tests
	PYTHONPATH=simulator/ssd/src $(PYTHON) -m ssd_sim.cli verify-profile simulator/ssd/profiles/$(SSD_SIM_PROFILE).yaml
	PYTHONPATH=simulator/ssd/src $(PYTHON) -m ssd_sim.cli campaign --profile simulator/ssd/profiles/$(SSD_SIM_PROFILE).yaml --seed $(SSD_SIM_SEED) --operations 200 --out artifacts/ssd-sim-campaign.json
storage-verify: build
	$(PYTHON) tools/run_storage_campaign.py --backend $(STORAGE_BACKEND) --profile $(STORAGE_PROFILE) --seed $(STORAGE_SEED)
