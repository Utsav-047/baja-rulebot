import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center text-center px-6 py-24">
        <div className="bg-orange-500 text-white font-bold px-4 py-2 rounded-xl text-sm mb-6 uppercase tracking-widest">
          AI Powered
        </div>
        <h1 className="text-5xl font-extrabold mb-4 leading-tight">
          BAJA <span className="text-orange-500">RuleBot</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-xl mb-10">
          Your AI assistant for BAJA SAEINDIA competition rules.
          Upload any rulebook and get instant answers, checklists, and compliance guidance.
        </p>
        <div className="flex gap-4">
          <button
            onClick={() => navigate('/upload')}
            className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-8 py-3 rounded-xl transition"
          >
            Upload Rulebook
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="border border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white font-bold px-8 py-3 rounded-xl transition"
          >
            Start Chatting
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 px-12 pb-20">
        <div className="bg-gray-800 rounded-2xl p-6">
          <div className="text-orange-500 text-3xl mb-3">📄</div>
          <h3 className="text-xl font-bold mb-2">Upload Any Rulebook</h3>
          <p className="text-gray-400 text-sm">Upload any version of BAJA rulebook PDF and the bot adapts instantly.</p>
        </div>
        <div className="bg-gray-800 rounded-2xl p-6">
          <div className="text-orange-500 text-3xl mb-3">💬</div>
          <h3 className="text-xl font-bold mb-2">Ask in Plain English</h3>
          <p className="text-gray-400 text-sm">No more searching through pages. Just ask your question naturally.</p>
        </div>
        <div className="bg-gray-800 rounded-2xl p-6">
          <div className="text-orange-500 text-3xl mb-3">✅</div>
          <h3 className="text-xl font-bold mb-2">Get Checklists</h3>
          <p className="text-gray-400 text-sm">Generate compliance checklists for technical inspection, billing, and safety.</p>
        </div>
      </div>
    </div>
  )
}

export default Home