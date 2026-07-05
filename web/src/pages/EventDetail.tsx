import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { ErrorState, FeedSkeleton } from "../components/States";
import { useEvent } from "../hooks/details";
import { categoryTone, formatTimeRange } from "../lib/format";

export function EventDetail() {
  const { id = "" } = useParams();
  const { data, isPending, isError, error, refetch } = useEvent(id);

  return (
    <article className="detail">
      <Link className="back" to="/events">
        ‹ Back to events
      </Link>

      {isPending && <FeedSkeleton count={1} />}

      {isError && (
        <ErrorState
          message={
            error instanceof ApiError && error.status === 404
              ? "This event doesn't exist or was removed."
              : error instanceof ApiError
                ? error.message
                : "Failed to load."
          }
          onRetry={() => refetch()}
        />
      )}

      {data && (
        <>
          {data.imageUrl && <img className="hero" src={data.imageUrl} alt="" />}
          <h1 className="detail-title">{data.title}</h1>
          <div className="detail-meta">
            <span className={`chip ${categoryTone(data.category)}`}>{data.category}</span>
            <span className="dot">·</span>
            <span>📍 {data.venue}</span>
            <span className="dot">·</span>
            <span>{formatTimeRange(data.startTime, data.endTime)}</span>
            <span className="dot">·</span>
            <span>{data.organizer}</span>
          </div>
          <hr />
          <div className="detail-body">{data.description}</div>
        </>
      )}
    </article>
  );
}
