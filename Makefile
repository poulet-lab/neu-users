# TODO test build
.PHONY: docker

MICROSERVICE=neu-users

APPVERSION := $(shell awk -F'\"' '/__version__/ {print $$2}' src/__init__.py)

GIT_SHA := $(shell git rev-parse HEAD)

ifeq ($(ENABLE_FULL_RELRO), "true")
	GOFLAGS += -ldflags "-bindnow"
endif

ifeq ($(ENABLE_PIE), "true")
	GOFLAGS += -buildmode=pie
endif

docker: 
	docker build \
		-f dockerfile \
		--label "git_sha=$(GIT_SHA)" \
		-t edgexfoundry/${MICROSERVICE}:$(APPVERSION) \
		.