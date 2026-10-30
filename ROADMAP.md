# Roadmap

Ordered by how often each job comes up, how painful the current workaround is, and how much it costs to build. The goal is to stop opening Smallpdf, iLovePDF and Acrobat for everyday PDF work, not to rebuild every Acrobat feature.

## Now: make the daily jobs one click

**1. One-step compress, merge and convert screens.** Most visits to Smallpdf are a single job: drop a file and get it back smaller. Paperbench can already do this, but it takes four controls. Add a drop zone that compresses straight away, shows "4.5 MB → 150 KB", and offers the download. *Small effort, used every week.*

**2. Install as an app (PWA).** Make it installable from the GitHub Pages site so it opens in its own window, works offline, and appears in Finder's "Open with" for PDFs. This removes the "where was that link" friction. *Small effort.*

**3. Real-file feedback loop.** Test it on your own PDFs, and turn every file that compresses poorly or breaks into a test case. The generated test files are a proxy, and real publisher and portal PDFs will find new edge cases. *Ongoing.*

## Next: the features that keep sending you elsewhere

**4. Conversions (PDF ↔ Word, PowerPoint).** The most-used feature you don't have yet. The two directions are different problems:

- **PDF → Word.** Read the text, fonts and positions with pdf.js, rebuild the paragraphs, and write a .docx in the browser. It works well for papers, letters and forms. Complex layouts come out approximate, which is true of Smallpdf too.
- **Word/PowerPoint → PDF.** Needs a full document layout engine, so you can't write it from scratch. Options:
  - **LibreOffice compiled to WebAssembly.** Stays private and in-browser, but it's a large one-time download (~50 MB, then cached). Spike this first.
  - **A small local helper that calls LibreOffice on your Mac.** Gives the best fidelity, but needs a one-off install.
  - **A conversion server.** Easiest to build, but files would leave your device, so rule it out.

  Note: Word and PowerPoint can already export to PDF themselves (File → Save As → PDF). The gap Paperbench fills is batch conversion and machines without Office.

**5. True redaction.** Remove the text and image data under a box, not just cover it. This is a must for clinical documents. It needs the engine upgrade (item 7) to do properly.

**6. Fill PDF forms.** Consent forms, HR and grant paperwork. pdf-lib can already fill AcroForm fields, so this is mostly UI. *Medium effort, high frequency.*

## Later: Acrobat-level foundations

**7. Swap the core to PDFium (WebAssembly).** It's the engine inside Chrome. It unlocks proper redaction, editable annotations, faster rendering for 100+ page files, and lays the groundwork for editing text in place. Its licence is permissive (BSD/Apache).

**8. OCR for scans** with Tesseract.js, which runs in the browser, so scanned PDFs become searchable and copyable.

**9. Edit existing text in place.** This is the hardest step, and even Acrobat struggles with some files. Depends on item 7.

**10. Font subsetting and deduplication** during compression, to shrink text-heavy PDFs that compression can't touch today.

## Not planned

- **Certificate-based digital signatures.** These need certificate management and are rarely required outside legal workflows.
- **Cloud storage or accounts.** They would undo the reason this exists.
