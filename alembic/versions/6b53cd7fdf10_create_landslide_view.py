"""create landslide view

Revision ID: 6b53cd7fdf10
Revises: 60c02345bd3d
Create Date: 2026-04-01 09:27:49.247174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b53cd7fdf10'
down_revision: Union[str, Sequence[str], None] = '60c02345bd3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW public.landslides_view AS
    SELECT
        l.id,
        l.datetime,
        l.report,
        l.report_source,
        l.report_url,
        l.original_classification,
        c.name AS classification_name,
        l.source_id,
        s.name AS source_name,
        s.doi AS source_doi,
        l.geometry
    FROM
        public.landslides l
    JOIN
        public.classification c ON l.classification_id = c.id
    JOIN
        public.sources s ON l.source_id = s.id;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.landslides_view;")