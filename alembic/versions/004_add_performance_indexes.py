"""Add performance indexes for hot query paths.

Addresses dashboard/order-search/payment-reconciliation lag by indexing the
columns that are filtered/sorted on most frequently: tenant-scoped listing
queries, customer lookups, and ledger/inventory joins.

Revision ID: 004_add_performance_indexes
Revises: 3f8a1c2e9b47
Create Date: 2026-07-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_performance_indexes'
down_revision = '3f8a1c2e9b47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Orders: tenant-scoped listing sorted by recency (dashboard, order list)
    op.create_index(
        'ix_orders_tenant_created_at',
        'orders',
        ['tenant_id', sa.text('created_at DESC')],
    )
    # Orders: customer-scoped lookups (credit limit aggregation, customer detail page)
    op.create_index(
        'ix_orders_customer_id',
        'orders',
        ['customer_id'],
    )

    # Invoices: customer-scoped lookups used by payment reconciliation/collections
    op.create_index(
        'ix_invoices_customer_created_at',
        'invoices',
        ['customer_id', 'created_at'],
    )

    # Payments: customer-scoped, most-recent-first (collections, reconciliation)
    op.create_index(
        'ix_payments_customer_created_at',
        'payments',
        ['customer_id', sa.text('created_at DESC')],
    )

    # Order state ledger: fetching current_status requires the latest row per order
    op.create_index(
        'ix_order_state_ledger_order_timestamp',
        'order_state_ledger',
        ['order_id', sa.text('timestamp DESC')],
    )

    # Inventory: looked up per line-item during order confirmation/deduction
    op.create_index(
        'ix_inventory_tenant_sku',
        'inventory',
        ['tenant_id', 'sku_id'],
    )

    # Customer aliases: WhatsApp sender-phone resolution on every inbound message
    op.create_index(
        'ix_customer_aliases_alias_value',
        'customer_aliases',
        ['alias_value'],
    )


def downgrade() -> None:
    op.drop_index('ix_customer_aliases_alias_value', table_name='customer_aliases')
    op.drop_index('ix_inventory_tenant_sku', table_name='inventory')
    op.drop_index('ix_order_state_ledger_order_timestamp', table_name='order_state_ledger')
    op.drop_index('ix_payments_customer_created_at', table_name='payments')
    op.drop_index('ix_invoices_customer_created_at', table_name='invoices')
    op.drop_index('ix_orders_customer_id', table_name='orders')
    op.drop_index('ix_orders_tenant_created_at', table_name='orders')
