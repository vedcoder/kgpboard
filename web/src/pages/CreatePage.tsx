// Admin-only page to create a notice or event, with a drag-drop poster upload.
// Flow: (optionally) upload the image -> create the item -> go to its detail.

import { useEffect, useMemo, useRef, useState } from "react";
import type { DragEvent, FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { ApiError, api } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import { useMeta } from "../hooks/meta";

type Kind = "notice" | "event";

export function CreatePage() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);

  const meta = useMeta();
  const [kind, setKind] = useState<Kind>("notice");
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [content, setContent] = useState(""); // notice
  const [description, setDescription] = useState(""); // event
  const [venue, setVenue] = useState("");
  const [organizer, setOrganizer] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [registrationUrl, setRegistrationUrl] = useState("");
  const [targetYear, setTargetYear] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const categoryOptions =
    kind === "notice"
      ? (meta.data?.noticeCategories ?? [])
      : (meta.data?.eventCategories ?? []);

  const preview = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  // Only admins may create. Wait for auth to resolve before deciding.
  if (isLoading) return null;
  if (!user || user.role !== "admin") return <Navigate to="/login" replace />;

  function onDrop(e: DragEvent) {
    e.preventDefault();
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) setFile(dropped);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      let imageUrl: string | undefined;
      if (file) {
        imageUrl = (await api.uploadImage(file)).url;
      }

      if (kind === "notice") {
        const notice = await api.createNotice({ title, content, category, imageUrl });
        await queryClient.invalidateQueries({ queryKey: ["notices"] });
        await queryClient.invalidateQueries({ queryKey: ["categories", "notices"] });
        navigate(`/notices/${notice.id}`);
      } else {
        const event = await api.createEvent({
          title,
          description,
          category,
          venue,
          organizer,
          startTime: new Date(start).toISOString(),
          endTime: new Date(end).toISOString(),
          imageUrl,
          registrationUrl: registrationUrl || undefined,
          targetYear: targetYear || undefined,
        });
        await queryClient.invalidateQueries({ queryKey: ["events"] });
        await queryClient.invalidateQueries({ queryKey: ["categories", "events"] });
        navigate(`/events/${event.id}`);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="create-wrap">
      <button type="button" className="back" onClick={() => navigate(-1)}>
        ‹ Back
      </button>
      <form className="auth-card create-card" onSubmit={onSubmit}>
        <h1>New {kind}</h1>

        <div className="segmented" role="tablist">
          <button
            type="button"
            className={kind === "notice" ? "active" : ""}
            onClick={() => {
              setKind("notice");
              setCategory("");
            }}
          >
            Notice
          </button>
          <button
            type="button"
            className={kind === "event" ? "active" : ""}
            onClick={() => {
              setKind("event");
              setCategory("");
            }}
          >
            Event
          </button>
        </div>

        {error && <div className="auth-error">{error}</div>}

        {/* Poster */}
        <div
          className="dropzone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          onClick={() => fileInput.current?.click()}
        >
          {preview ? (
            <img className="poster-preview" src={preview} alt="Poster preview" />
          ) : (
            <div className="dz-empty">
              <span className="dz-ico">🖼️</span>
              <p>Drag a poster here, or click to choose</p>
              <small>JPG, PNG or WebP · up to 5 MB · optional</small>
            </div>
          )}
          <input
            ref={fileInput}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            hidden
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
        {file && (
          <button type="button" className="link-btn remove-poster" onClick={() => setFile(null)}>
            Remove image
          </button>
        )}

        <div className="field">
          <label htmlFor="title">Title</label>
          <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>

        <div className="field">
          <label htmlFor="category">Category</label>
          <div className="select block">
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              required
            >
              <option value="" disabled>
                Choose a category…
              </option>
              {categoryOptions.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {kind === "notice" ? (
          <div className="field">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={5}
              required
            />
          </div>
        ) : (
          <>
            <div className="field">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="venue">Venue</label>
              <input id="venue" value={venue} onChange={(e) => setVenue(e.target.value)} required />
            </div>
            <div className="field">
              <label htmlFor="organizer">Organizer</label>
              <input
                id="organizer"
                value={organizer}
                onChange={(e) => setOrganizer(e.target.value)}
                placeholder="e.g. Robotics Club"
                required
              />
            </div>
            <div className="form-row">
              <div className="field">
                <label htmlFor="start">Starts</label>
                <input
                  id="start"
                  type="datetime-local"
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="end">Ends</label>
                <input
                  id="end"
                  type="datetime-local"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="field">
              <label htmlFor="targetYear">Target year (optional)</label>
              <div className="select block">
                <select
                  id="targetYear"
                  value={targetYear}
                  onChange={(e) => setTargetYear(e.target.value)}
                >
                  <option value="">Not specified</option>
                  {(meta.data?.targetYears ?? []).map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="field">
              <label htmlFor="registrationUrl">Registration link (optional)</label>
              <input
                id="registrationUrl"
                type="url"
                value={registrationUrl}
                onChange={(e) => setRegistrationUrl(e.target.value)}
                placeholder="https://forms.gle/…"
              />
            </div>
          </>
        )}

        <button className="btn primary block" disabled={busy}>
          {busy ? "Publishing…" : `Publish ${kind}`}
        </button>
      </form>
    </div>
  );
}
