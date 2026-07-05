import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { ErrorState, FeedSkeleton } from "../components/States";
import { useNotice } from "../hooks/details";
import { categoryTone, formatDate } from "../lib/format";

export function NoticeDetail() {
  const { id = "" } = useParams();
  const { data, isPending, isError, error, refetch } = useNotice(id);

  return (
    <article className="detail">
      <Link className="back" to="/">
        ‹ Back to notices
      </Link>

      {isPending && <FeedSkeleton count={1} />}

      {isError && (
        <ErrorState
          message={
            error instanceof ApiError && error.status === 404
              ? "This notice doesn't exist or was removed."
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
            <span>{data.postedBy.name}</span>
            <span className="dot">·</span>
            <span>{formatDate(data.createdAt)}</span>
          </div>
          <hr />
          <div className="detail-body">{data.content}</div>
        </>
      )}
    </article>
  );
}
