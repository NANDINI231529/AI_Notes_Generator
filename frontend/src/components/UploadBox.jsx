import { FileText, Image, UploadCloud } from "lucide-react";

export default function UploadBox({ file, onFileChange, onUpload, loading }) {
  return (
    <section className="upload-box">
      <div className="upload-icon">
        <UploadCloud size={42} />
      </div>
      <h2>Upload a document</h2>
      <p>PDF, DOCX, TXT, JPG, and PNG files are supported.</p>
      <label className="file-input">
        <input
          type="file"
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
          onChange={(event) => onFileChange(event.target.files?.[0] || null)}
        />
        <span>{file ? file.name : "Choose file"}</span>
      </label>
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
      <button className="primary wide" disabled={!file || loading} onClick={onUpload}>
        {loading ? "Processing..." : "Extract Text & Generate Notes"}
      </button>
    </section>
  );
}
