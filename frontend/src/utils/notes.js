export function cleanNoteText(text = "") {
  return text.replace(/^#{1,6}\s*/gm, "");
}
