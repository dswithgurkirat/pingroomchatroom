-- ================================================================
--  PingRoom — Supabase Database Schema
--  Run this in: Supabase Dashboard → SQL Editor
-- ================================================================

-- Enable UUID extension (already on in Supabase by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── rooms ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rooms (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    created_by  UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── messages ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    room_id     UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    message     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_room_id    ON messages (room_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id    ON messages (user_id);

-- ── stickers ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stickers (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    price       NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    url         TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── purchases ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS purchases (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    sticker_id  UUID NOT NULL REFERENCES stickers(id) ON DELETE CASCADE,
    payment_id  TEXT NOT NULL UNIQUE,         -- Stripe payment_intent or session id
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, sticker_id)              -- one purchase per sticker per user
);

CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases (user_id);

-- ================================================================
--  Row-Level Security (RLS)
-- ================================================================

ALTER TABLE rooms     ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages  ENABLE ROW LEVEL SECURITY;
ALTER TABLE stickers  ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;

-- ── rooms policies ───────────────────────────────────────────────
CREATE POLICY "Anyone authenticated can view rooms"
    ON rooms FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can create rooms"
    ON rooms FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Room creator can delete their room"
    ON rooms FOR DELETE
    USING (auth.uid() = created_by);

-- ── messages policies ────────────────────────────────────────────
CREATE POLICY "Authenticated users can read messages"
    ON messages FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can send messages"
    ON messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own messages"
    ON messages FOR DELETE
    USING (auth.uid() = user_id);

-- ── stickers policies ────────────────────────────────────────────
CREATE POLICY "Anyone authenticated can view stickers"
    ON stickers FOR SELECT
    USING (auth.role() = 'authenticated');

-- Sticker creation is restricted to service-role (admin backend only).
-- The service_role key bypasses RLS entirely — no INSERT policy needed.

-- ── purchases policies ───────────────────────────────────────────
CREATE POLICY "Users can view their own purchases"
    ON purchases FOR SELECT
    USING (auth.uid() = user_id);

-- Inserts are done by the service-role key from the webhook, bypassing RLS.

-- ================================================================
--  Seed — Sample stickers (optional)
-- ================================================================
INSERT INTO stickers (name, price, url) VALUES
    ('🔥 Fire Pack',    1.99, 'https://example.com/stickers/fire.png'),
    ('💎 Diamond Pack', 4.99, 'https://example.com/stickers/diamond.png'),
    ('🚀 Rocket Pack',  2.99, 'https://example.com/stickers/rocket.png')
ON CONFLICT DO NOTHING;
