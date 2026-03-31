"""create landslide view

Revision ID: 7ee3f99f3f2d
Revises: 54f61396c023
Create Date: 2026-03-31 16:53:31.934240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ee3f99f3f2d'
down_revision: Union[str, Sequence[str], None] = '54f61396c023'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW public.landslides_view AS
    SELECT
        l.id,
        l.date,
        l.report,
        l.report_source,
        l.report_url,
        l.original_classification,
        c.name AS classification_name,
        l.source_id,
        s.name AS source_name,
        s.doi AS source_doi,
        l.geom
    FROM
        public.landslides l
    JOIN
        public.classification c ON l.classification_id = c.id
    JOIN
        public.sources s ON l.source_id = s.id;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.landslides_view;")