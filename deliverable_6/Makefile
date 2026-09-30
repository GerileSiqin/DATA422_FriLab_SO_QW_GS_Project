PYTHON ?= python3
DOCUMENT_PYTHON ?= $(PYTHON)
.PHONY: all run test documents sanity verify

all: documents

run:
	"$(PYTHON)" run_pipeline.py

test:
	"$(PYTHON)" -m unittest discover -s tests -v

documents: verify
	"$(DOCUMENT_PYTHON)" tools/build_documents.py

sanity: run
	"$(PYTHON)" sanity_check_example.py

verify: run sanity
	"$(PYTHON)" tools/verify_delivery.py
