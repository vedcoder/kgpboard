// A single feed row (notice or event), linking to its detail page.

import { Link } from "react-router-dom";
import { categoryTone } from "../lib/format";

interface Props {
  to: string;
  title: string;
  category: string;
  date: string;
  venue?: string; // events only
  imageUrl?: string | null;
}

export function FeedCard({ to, title, category, date, venue, imageUrl }: Props) {
  return (
    <Link className="card" to={to}>
      {imageUrl && (
        <img className="card-thumb" src={imageUrl} alt="" loading="lazy" />
      )}
      <div className="card-body">
        <p className="card-title">{title}</p>
        <div className="card-meta">
          <span className={`chip ${categoryTone(category)}`}>{category}</span>
          {venue && <span>📍 {venue}</span>}
        </div>
      </div>
      <span className="card-date">{date}</span>
      <span className="chev" aria-hidden="true">
        ›
      </span>
    </Link>
  );
}
