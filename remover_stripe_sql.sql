-- Script SQL para remover campos do Stripe do banco de dados PostgreSQL

-- Remover colunas da tabela gestao_rural_assinaturacliente
ALTER TABLE gestao_rural_assinaturacliente DROP COLUMN IF EXISTS stripe_customer_id;
ALTER TABLE gestao_rural_assinaturacliente DROP COLUMN IF EXISTS stripe_subscription_id;

-- Remover coluna da tabela gestao_rural_planoassinatura
ALTER TABLE gestao_rural_planoassinatura DROP COLUMN IF EXISTS stripe_price_id;

-- Remover índices relacionados ao Stripe
DROP INDEX IF EXISTS gestao_rura_stripe__c9bd88_idx;
DROP INDEX IF EXISTS gestao_rura_stripe__5b5809_idx;
DROP INDEX IF EXISTS gestao_rura_stripe__628be9_idx;
DROP INDEX IF EXISTS gestao_rura_stripe__9724d3_idx;







