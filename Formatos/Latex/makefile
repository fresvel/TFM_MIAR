MAINDOC = main
BUILD_DIR = build
OUT_DIR = out

TEX = xelatex
BIBTEX = bibtex
TEXFLAGS = -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR)

SOURCES = $(MAINDOC).tex \
	preambulo/preambulo.tex \
	$(shell find secciones -type f -name '*.tex') \
	bibliografia.bib \
	$(wildcard assets/tablas/*.tex) \
	$(wildcard assets/algoritmos/*.tex) \
	$(wildcard assets/figuras/*) \
	$(wildcard assets/figuras/branding/*)

PDF = $(OUT_DIR)/$(MAINDOC).pdf
REPORT = $(OUT_DIR)/report.pdf

all: $(PDF)

$(BUILD_DIR) $(OUT_DIR):
	mkdir -p $@

$(PDF): $(SOURCES) | $(BUILD_DIR) $(OUT_DIR)
	$(TEX) $(TEXFLAGS) $(MAINDOC).tex
	$(BIBTEX) $(BUILD_DIR)/$(MAINDOC)
	$(TEX) $(TEXFLAGS) $(MAINDOC).tex
	$(TEX) $(TEXFLAGS) $(MAINDOC).tex
	cp $(BUILD_DIR)/$(MAINDOC).pdf $(PDF)

report: $(REPORT)

$(REPORT): $(PDF) | $(OUT_DIR)
	gs -o $@ -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 $(PDF)

clean:
	@rm -rf $(BUILD_DIR) $(OUT_DIR)
	@rm -f *.bbl *.blg *.dvi *~ *.ps *.aux *.log *.pdf *.bak *.toc *.lof *.lot *.out *.fls *.fdb_latexmk *.run.xml
