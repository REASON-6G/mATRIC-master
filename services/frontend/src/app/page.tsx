export default function Home() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded shadow">Connected Agents: 5</div>
        <div className="p-4 bg-white rounded shadow">Active Topics: 12</div>
        <div className="p-4 bg-white rounded shadow">Messages Processed: 12345</div>
      </div>
      <div className="p-4 bg-white rounded shadow h-96">
        Map placeholder (Publisher locations)
      </div>
      <div className="p-4 bg-white rounded shadow h-96">
        Topics directory
      </div>
    </div>
  );
}