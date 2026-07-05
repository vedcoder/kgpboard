import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { AdminUsers } from "./pages/AdminUsers";
import { CreatePage } from "./pages/CreatePage";
import { Dashboard } from "./pages/Dashboard";
import { EventDetail } from "./pages/EventDetail";
import { Login } from "./pages/Login";
import { NoticeDetail } from "./pages/NoticeDetail";
import { Signup } from "./pages/Signup";

function NotFound() {
  return (
    <div className="state">
      <div className="ico">🧭</div>
      <h3>Page not found</h3>
      <p>The page you’re looking for doesn’t exist.</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Header />
        <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard kind="notices" />} />
          <Route path="/notices" element={<Dashboard kind="notices" />} />
          <Route path="/events" element={<Dashboard kind="events" />} />
          <Route path="/notices/:id" element={<NoticeDetail />} />
          <Route path="/events/:id" element={<EventDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/admin/users" element={<AdminUsers />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
