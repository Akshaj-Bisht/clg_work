# Practical 4 work log

## Goal
Convert the classmate's Practical 4 Wireshark PDF into an Obsidian Markdown practical, following the layout of `PRAC 3/Practical 3.md`, and include the useful screenshots from the PDF.

## Steps completed
1. Read `pdfs/Practical 4 - Analyze network packets using Wireshark (1).pdf` and checked the subject guidelines in `Guidelines_CyberForensics.pdf`.
2. Compared the note structure with `PRAC 3/Practical 3.md`.
3. Wrote `Practical 4.md` with the aim, requirements, Wireshark overview, procedure, display filters, protocol notes, analysis summary, and conclusion.
4. Extracted the six embedded Wireshark screenshots from the PDF into `images/` and added Obsidian embeds at the matching sections.
5. Improved the note against the subject guidelines by distinguishing capture and display filters, adding a capture/evidence-handling workflow, and clarifying that the supplied screenshots are examples rather than a new local capture.

## Screenshot map
- `images/practical-4-000.png` — DNS filter and packet details
- `images/practical-4-001.png` — TCP packet list
- `images/practical-4-002.png` — TCP SYN filter results
- `images/practical-4-003.png` — TLS packet list and handshake details
- `images/practical-4-004.png` — IP packet list and details
- `images/practical-4-005.png` — ICMP Echo Request/Reply and fields

## Tool note
The requested PdfCraft MCP is not exposed among the tools available in this session. The official PdfCraft MCP guide describes its stdio server and `command_run` interface, but it must be installed and registered with the client before those MCP tools can be called. For this task, the PDF's embedded images were extracted locally with Poppler's `pdfimages` utility.

## Status
- Markdown practical: complete
- PDF screenshots: extracted and embedded
- Screenshot files are local assets in this folder
- No separate packet capture (`.pcap`/`.pcapng`) was supplied; the note describes analysis of the examples shown in the PDF.
