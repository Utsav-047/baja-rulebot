import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const navigate = useNavigate()

  const handleFile = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = () => {
    if (!file) return
    setUploading(true)
    setTimeout(() => {
      setUploading(false)
      setUploaded(true)
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-6">
      <h2 className="text-4xl font-bold mb-2">Upload <span className="text-orange-500">Rulebook</span></h2>
      <p className="text-gray-400 mb-10">Upload the BAJA competition rulebook PDF to get started</p>

      <div className="bg-gray-800 rounded-2xl p-10 w-full max-w-lg text-center">
        <div className="text-6xl mb-4">📂</div>
        <p className="text-gray-400 mb-6 text-sm">Supported format: PDF only</p>

        <input
          type="file"
          accept=".pdf"
          onChange={handleFile}
          className="hidden"
          id="fileInput"
        />
        <label
          htmlFor="fileInput"
          className="cursor-pointer bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-xl transition block mb-4"
        >
          {file ? file.name : 'Choose PDF File'}
        </label>

        {file && !uploaded && (
          <button
            onClick={handleUpload}
            className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-8 py-3 rounded-xl transition w-full"
          >
            {uploading ? 'Uploading...' : 'Upload Rulebook'}
          </button>
        )}

        {uploaded && (
          <div>
            <p className="text-green-400 font-bold mb-4">✅ Rulebook Uploaded Successfully!</p>
            <button
              onClick={() => navigate('/chat')}
              className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-8 py-3 rounded-xl transition w-full"
            >
              Go to Chat →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Upload