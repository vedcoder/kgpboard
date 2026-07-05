// Presentational wrapper: given the status of a feed, shows the right thing
// (skeleton / error / empty / list + "Load more"). Kept prop-based (not
// generic) so it's simple and fully typed.

import type { ReactNode } from "react";
import { EmptyState, ErrorState, FeedSkeleton } from "./States";

interface Props {
  isPending: boolean;
  isError: boolean;
  errorMessage: string;
  onRetry: () => void;
  isEmpty: boolean;
  emptyMessage: string;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
  children: ReactNode; // the rendered cards
}

export function FeedView({
  isPending,
  isError,
  errorMessage,
  onRetry,
  isEmpty,
  emptyMessage,
  hasMore,
  isLoadingMore,
  onLoadMore,
  children,
}: Props) {
  if (isPending) return <FeedSkeleton />;
  if (isError) return <ErrorState message={errorMessage} onRetry={onRetry} />;
  if (isEmpty) return <EmptyState message={emptyMessage} />;

  return (
    <>
      <div className="feed">{children}</div>
      {hasMore && (
        <div className="loadmore">
          <button onClick={onLoadMore} disabled={isLoadingMore}>
            {isLoadingMore ? "Loading…" : "Load more"}
          </button>
        </div>
      )}
    </>
  );
}
