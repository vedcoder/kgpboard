// A vertical feed card (notice or event), linking to its detail page.
// Every card has an image area; without a poster it shows a placeholder.

import { Link } from "react-router-dom";
import { categoryEmoji, categoryTone } from "../lib/format";

interface Props {
  to: string;
  title: string;
  category: string;
  date: string;
  excerpt: string;
  meta: string; // venue (events) or author (notices)
  imageUrl?: string | null;
}

export function FeedCard({ to, title, category, date, excerpt, meta, imageUrl }: Props) {
  const tone = categoryTone(category);
  return (
    <Link className="card" to={to}>
      <div className="card-image">
        {imageUrl ? (
          <img src={imageUrl} alt="" loading="lazy" />
        ) : (
          <div className={`card-image-empty ${tone}`}>
            <span className="emoji" aria-hidden="true">
              {categoryEmoji(category)}
            </span>
          </div>
        )}
        <span className={`chip overlay ${tone}`}>{category}</span>
      </div>
      <div className="card-content">
        <p className="card-title">{title}</p>
        <p className="card-excerpt">{excerpt}</p>
        <div className="card-meta">
          <span className="venue">{meta}</span>
          <span className="date">{date}</span>
        </div>
      </div>
    </Link>
  );
}
