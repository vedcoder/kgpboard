// Loading / error / empty views shared by the feeds and detail pages.

export function FeedSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="feed" aria-busy="true" aria-label="Loading">
      {Array.from({ length: count }).map((_, i) => (
        <div className="skeleton" key={i} />
      ))}
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state error" role="alert">
      <div className="ico">⚠️</div>
      <h3>Something went wrong</h3>
      <p>{message}</p>
      {onRetry && (
        <button className="retry" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="state">
      <div className="ico">🗂️</div>
      <h3>Nothing here</h3>
      <p>{message}</p>
    </div>
  );
}
