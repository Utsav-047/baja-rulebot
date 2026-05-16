// function Navbar() {
//   return (
//     <nav className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-lg">
//       <div className="flex items-center gap-3">
//         <div className="bg-orange-500 text-white font-bold px-3 py-1 rounded-lg text-lg">
//           BAJA
//         </div>
//         <span className="text-xl font-bold">RuleBot</span>
//       </div>
//       <div className="flex gap-6 text-sm">
//         <a href="/" className="hover:text-orange-400 transition">Home</a>
//         <a href="/upload" className="hover:text-orange-400 transition">Upload Rulebook</a>
//         <a href="/chat" className="hover:text-orange-400 transition">Chat</a>
//       </div>
//     </nav>
//   )
// }

// export default Navbar


function Navbar() {
  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-3">
        <div className="bg-orange-500 text-white font-bold px-3 py-1 rounded-lg text-lg">
          BAJA
        </div>
        <span className="text-xl font-bold">RuleBot</span>
      </div>
      <div className="flex gap-6 text-sm">
        <a href="/" className="hover:text-orange-400 transition">Home</a>
        <a href="/upload" className="hover:text-orange-400 transition">Upload Rulebook</a>
        <a href="/chat" className="hover:text-orange-400 transition">Chat</a>
      </div>
    </nav>
  )
}

export default Navbar