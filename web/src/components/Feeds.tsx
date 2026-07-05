// Feed components: each binds its data hook to the presentational FeedView.
// Only the mounted one runs its query, so the inactive tab costs nothing.

import { ApiError } from "../api/client";
import type { FeedFilters } from "../hooks/feeds";
import { useEvents, useNotices } from "../hooks/feeds";
import { formatDate } from "../lib/format";
import { FeedCard } from "./FeedCard";
import { FeedView } from "./FeedView";

function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : "Failed to load. Please retry.";
}

export function NoticesFeed({ filters }: { filters: FeedFilters }) {
  const query = useNotices(filters);
  const items = query.data?.pages.flatMap((p) => p.items) ?? [];

  return (
    <FeedView
      isPending={query.isPending}
      isError={query.isError}
      errorMessage={errorMessage(query.error)}
      onRetry={() => query.refetch()}
      isEmpty={items.length === 0}
      emptyMessage="No notices match your search."
      hasMore={!!query.hasNextPage}
      isLoadingMore={query.isFetchingNextPage}
      onLoadMore={() => query.fetchNextPage()}
    >
      {items.map((n) => (
        <FeedCard
          key={n.id}
          to={`/notices/${n.id}`}
          title={n.title}
          category={n.category}
          excerpt={n.content}
          meta={`by ${n.postedBy.name}`}
          date={formatDate(n.createdAt)}
          imageUrl={n.imageUrl}
        />
      ))}
    </FeedView>
  );
}

export function EventsFeed({ filters }: { filters: FeedFilters }) {
  const query = useEvents(filters);
  const items = query.data?.pages.flatMap((p) => p.items) ?? [];

  return (
    <FeedView
      isPending={query.isPending}
      isError={query.isError}
      errorMessage={errorMessage(query.error)}
      onRetry={() => query.refetch()}
      isEmpty={items.length === 0}
      emptyMessage="No events match your search."
      hasMore={!!query.hasNextPage}
      isLoadingMore={query.isFetchingNextPage}
      onLoadMore={() => query.fetchNextPage()}
    >
      {items.map((e) => (
        <FeedCard
          key={e.id}
          to={`/events/${e.id}`}
          title={e.title}
          category={e.category}
          excerpt={e.description}
          meta={`📍 ${e.venue}`}
          date={formatDate(e.startTime)}
          imageUrl={e.imageUrl}
        />
      ))}
    </FeedView>
  );
}
