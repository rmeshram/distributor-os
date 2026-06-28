"""add order status and indexes

Revision ID: 5cdd58b4bf04
Revises: 2c336cf57c66
Create Date: 2026-06-28 16:29:32.836214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cdd58b4bf04'
down_revision: Union[str, Sequence[str], None] = '2c336cf57c66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=False, server_default='Draft'))

    # Backfill statuses from the latest OrderStateLedger entries
    connection = op.get_bind()
    orders_ledger = connection.execute(sa.text(
        "SELECT order_id, to_status FROM order_state_ledger AS osl "
        "WHERE osl.timestamp = ("
        "  SELECT MAX(timestamp) FROM order_state_ledger "
        "  WHERE order_id = osl.order_id"
        ")"
    )).fetchall()
    
    for row in orders_ledger:
        connection.execute(
            sa.text("UPDATE orders SET status = :status WHERE id = :order_id"),
            {"status": row[1], "order_id": row[0]}
        )

    # Add indexes
    op.create_index('ix_orders_tenant_id', 'orders', ['tenant_id'])
    op.create_index('ix_order_line_items_tenant_id', 'order_line_items', ['tenant_id'])
    op.create_index('ix_order_state_ledger_tenant_id', 'order_state_ledger', ['tenant_id'])
    op.create_index('ix_customers_tenant_id', 'customers', ['tenant_id'])
    op.create_index('ix_products_tenant_id', 'products', ['tenant_id'])
    op.create_index('ix_invoices_tenant_id', 'invoices', ['tenant_id'])
    
    op.create_index('ix_order_state_ledger_order_id_timestamp', 'order_state_ledger', ['order_id', 'timestamp'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    op.create_index('ix_order_line_items_order_id', 'order_line_items', ['order_id'])
    op.create_index('ix_invoices_order_id', 'invoices', ['order_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_invoices_order_id', table_name='invoices')
    op.drop_index('ix_order_line_items_order_id', table_name='order_line_items')
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_order_state_ledger_order_id_timestamp', table_name='order_state_ledger')
    
    op.drop_index('ix_invoices_tenant_id', table_name='invoices')
    op.drop_index('ix_products_tenant_id', table_name='products')
    op.drop_index('ix_customers_tenant_id', table_name='customers')
    op.drop_index('ix_order_state_ledger_tenant_id', table_name='order_state_ledger')
    op.drop_index('ix_order_line_items_tenant_id', table_name='order_line_items')
    op.drop_index('ix_orders_tenant_id', table_name='orders')
    
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('status')
