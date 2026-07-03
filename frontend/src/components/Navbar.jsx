export default function Navbar({ setPage }) {
  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 
          className="text-2xl font-bold cursor-pointer hover:text-blue-200" 
          onClick={() => setPage('home')}
        >
          Policy Intelligence
        </h1>
        <div className="space-x-4">
          <button 
            onClick={() => setPage('home')} 
            className="hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            Home
          </button>
          <button 
            onClick={() => setPage('query')} 
            className="hover:bg-blue-700 px-3 py-2 rounded transition"
          >
            Query
          </button>
        </div>
      </div>
    </nav>
  );
}
