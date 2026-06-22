import { FileText, Image, UploadCloud, X } from "lucide-react";

export default function UploadBox({ files, onFilesChange, onUpload, loading }) {
  const selectedFiles = files || [];

  const removeFile = (indexToRemove) => {
    onFilesChange(selectedFiles.filter((_, index) => index !== indexToRemove));
  };

  return (
    <section className="upload-box">
      <div className="upload-icon">
        <UploadCloud size={42} />
      </div>
      <h2>Upload study files</h2>
      <p>Add multiple PDFs, DOCX, TXT, JPG, JPEG, or PNG files in one batch.</p>
      <label className="file-input">
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
          onChange={(event) => onFilesChange(Array.from(event.target.files || []))}
        />
        <span>{selectedFiles.length ? `${selectedFiles.length} files selected` : "Choose files"}</span>
      </label>
      {selectedFiles.length > 0 && (
        <ul className="selected-files" aria-label="Selected files">
          {selectedFiles.map((selectedFile, index) => (
            <li key={`${selectedFile.name}-${selectedFile.lastModified}`}>
              <span>{selectedFile.name}</span>
              <button
                type="button"
                className="remove-file"
                aria-label={`Remove ${selectedFile.name}`}
                onClick={() => removeFile(index)}
              >
                <X size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="file-types">
        <span>
          <FileText size={16} />
          PDF DOCX TXT
        </span>
        <span>
          <Image size={16} />
          JPG PNG
        </span>
      </div>
      <button className="primary wide" disabled={!selectedFiles.length || loading} onClick={onUpload}>
        {loading ? "Processing..." : "Extract Text & Generate Notes"}
      </button>
    </section>
  );
}
