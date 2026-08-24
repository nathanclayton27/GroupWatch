-- clubd — friend privacy: the way out of being read (CLU-118)
--
-- Run ONCE in the Supabase SQL editor. Additive, and safe to re-run.
--
-- ===========================================================================
-- RUN ORDER — READ THIS FIRST. RUN THE SQL FIRST, THEN DEPLOY THE FRONT END.
-- ===========================================================================
--
-- Both orders are safe. Neither breaks the site. But run this first if you
-- can, and here is exactly what each direction does, so the choice is made on
-- fact rather than nerve:
--
--   SQL first, front end after (RECOMMENDED). The columns arrive carrying
--   today's behaviour to the letter — share_progress true, share_activity
--   true, hidden_slugs empty — so every friend sees on the morning after
--   precisely what they saw the night before. When the new build lands, the
--   switches are already backed by a database that honours them.
--
--   Front end first, SQL after (SAFE, just inert). The page asks the database
--   for its settings through privacy_settings(). Until this file runs that
--   function does not exist, the call errors, and every privacy control stays
--   HIDDEN — not greyed out, not present-and-broken, absent — the same way
--   friend names rendered before the shelf policy existed (CLU-72). Nothing
--   on the page can imply a privacy the database is not enforcing.
--
-- That last sentence is the whole ordering rule, and it is the one that
-- matters: a build must never draw these switches before this file has run.
-- It cannot. They are gated on the RPCs below answering — not on a version
-- number, not on a flag somebody has to remember to flip. clubd has shipped a
-- door with nothing behind it once already (the friend-code share links);
-- this is the same mistake refusing to be possible twice.
--
-- ===========================================================================
-- THE GAP THIS CLOSES
-- ===========================================================================
--
-- migrate-add-friend-shelves.sql (CLU-72) let mutual friends read each
-- other's progress rows. That was all it was asked to do, and it did it. But
-- friends are live on clubd.watch now, reading each other's shelves, and
-- there is no way to say no — not a switch that hides the shelf in the
-- browser, not a switch at all. That is the gap. Real people are inside it.
--
-- Three settings close it, and all three live on the row owner's profile,
-- because a setting the reader's browser holds is not a setting, it is a
-- suggestion:
--
--   share_progress   the master switch. Off, your shelves render nowhere on
--                    any friend's friends page. The friendship survives —
--                    they keep your name, you keep theirs. Default TRUE,
--                    which is today's behaviour, so nobody's experience
--                    changes until they choose to change it.
--
--   hidden_slugs     per list. Hidden here, that one list is gone from every
--                    friend's view and the rest stay. Set from the list's own
--                    page, where the context is; listed back on the account
--                    page, because a list hidden invisibly is a trap.
--
--   share_activity   consent, banked ahead of the feature. CLU-70 will put
--                    friends' live ticks and usernames into the activity
--                    feed. NOTHING READS THIS COLUMN YET — no policy below
--                    touches it. It exists so that when CLU-70 lands, the
--                    permission is already sitting there, set by the person
--                    it belongs to, instead of being retrofitted onto
--                    something that has already been public for a month.
--
--                    CLU-70 MUST GATE ON share_progress AND share_activity
--                    TOGETHER. A person who turned progress off has said no
--                    to the louder thing already; publishing their ticks
--                    because they never found this second switch would be
--                    the same betrayal wearing a different noun.
--
--                    Its default is TRUE, deliberately, and this is the one
--                    judgement call in the file worth a second look. TRUE
--                    means the feed has something in it the day it ships and
--                    that anyone who wants out could already have opted out,
--                    weeks before. FALSE means the feed launches empty and
--                    fills up only as people find the switch. If you want
--                    FALSE, change the single word `true` on the
--                    share_activity column below BEFORE you run this file —
--                    afterwards it is an UPDATE across every existing row and
--                    a different conversation.
--
-- ===========================================================================
-- WHAT IS DELIBERATELY NOT TOUCHED: CLUBS
-- ===========================================================================
--
-- Joining a club with a shared code is its own act of consent. You handed
-- somebody six characters; hiding a list from friends is not a retraction of
-- that. So a club's stack keeps showing your layer on a list you have hidden
-- from friends, and that is correct, not a leak.
--
-- The mechanism is PostgreSQL's, not a special case written here: multiple
-- PERMISSIVE policies on the same table and command are combined with OR. The
-- progress table carries four SELECT policies —
--
--   "read own"                  auth.uid() = user_id            (schema.sql)
--   "read group progress"       shares_group_with(...)          (schema.sql)
--   "mutual friends read progress"                              (CLU-72, and
--                               the only one this file rewrites)
--
-- — and a row comes back if ANY of them says yes. Narrowing the friends
-- policy therefore cannot narrow the club path: the club path is a different
-- OR branch and this file never names it. Nothing here mentions groups or
-- group_members, and nothing here should ever start to.
--
-- The visible consequence, stated plainly so it is not a surprise later: a
-- friend who is ALSO in a club with you, on that same list, still sees your
-- progress there — through the club, in the club's stack, where they were
-- always going to see it. Hiding a list from friends is not a way to hide
-- from a club. Leaving the club is.
--
-- ===========================================================================
-- WHY THE NEW COLUMNS ARE NOT READABLE BY OTHER PEOPLE
-- ===========================================================================
--
-- profiles is readable by every signed-in user — that is the CLU-69 design,
-- and it has to be, because a typed friend code has to find its owner. Left
-- alone, that would make hidden_slugs public: any signed-in stranger could
-- read the exact list of lists you were embarrassed enough to hide. A privacy
-- feature that publishes the privacy settings is not one.
--
-- So SELECT on profiles is narrowed to the four columns the handshake
-- actually needs, and the three new ones are reachable only through the
-- SECURITY DEFINER functions below — which answer about YOU (privacy_settings
-- reads auth.uid() and nobody else) or about a person who has already made
-- you a mutual friend (friend_may_read, whose answer the policy would have
-- given you anyway, so it is no kind of oracle).
--
-- The one-line undo, if a column grant ever gets in the way:
--
--     grant select on public.profiles to anon, authenticated;
--
-- It restores the old blanket read — and re-opens the hidden_slugs leak, so
-- do not leave it there.
--
-- Note for whoever adds the NEXT column to profiles: it will not be readable
-- until you add it to the grant below. That is the point, but it is the kind
-- of point that costs an hour if nobody wrote it down.

-- ---------------------------------------------------------------- columns --

alter table public.profiles
  add column if not exists share_progress boolean not null default true,
  add column if not exists share_activity boolean not null default true,
  add column if not exists hidden_slugs   text[]  not null default '{}';

-- The handshake needs a code, a name and an owner. It has never needed more,
-- and the three columns above are nobody's business but their owner's.
revoke select on public.profiles from anon, authenticated;
grant select (user_id, fcode, username, updated_at)
  on public.profiles to anon, authenticated;

-- ----------------------------------------------------------- the gatekeeper --

-- The CLU-72 condition with the owner's own answer bolted onto the end. It
-- lives in a SECURITY DEFINER function for one reason: the policy has to read
-- share_progress and hidden_slugs, and the grant above means the person
-- running the query cannot. The definer runs as the table owner, which can.
--
-- The mutual-friendship test stays inside rather than in the policy so that
-- the function is safe to leave callable: asked about a stranger it answers
-- false, which is exactly what the policy would have said. Two index lookups
-- on a two-column primary key is a cheap price for a function nobody can turn
-- into a directory of who is hiding what.
--
-- split_part on '#' is not decoration. A fresh watch (CLU-46) stores its
-- parallel run under `slug#fw`, a real row with a real property_id, and
-- hiding a list has to hide its rewatch too — otherwise the one list somebody
-- most wanted covered is the one still being served.
create or replace function public.friend_may_read(p_owner uuid, p_prop text)
returns boolean language sql security definer stable set search_path = public as $$
  select
    exists (select 1 from public.friendships f1
            where f1.a = auth.uid() and f1.b = p_owner)
    and
    exists (select 1 from public.friendships f2
            where f2.a = p_owner and f2.b = auth.uid())
    and
    coalesce((select p.share_progress
                     and not (split_part(p_prop, '#', 1) = any (p.hidden_slugs))
                from public.profiles p
               where p.user_id = p_owner), false);
$$;

-- ------------------------------------------------------------- the policy --

-- Replaced rather than altered so the file reads as one statement of what the
-- rule now is, and so re-running it lands the same rule every time.
--
-- This is the enforcement. Not the page: there is deliberately no filter in
-- src/template.html for a browser to skip past, because a browser that can
-- fetch the rows can print them however it likes. What is hidden here never
-- reaches the wire.
drop policy if exists "mutual friends read progress" on public.progress;
create policy "mutual friends read progress" on public.progress
  for select using (public.friend_may_read(progress.user_id, progress.property_id));

-- ---------------------------------------------------------------- the rpcs --

-- Reading and writing your own settings goes through these, not through the
-- table, because the grant above means the table will not answer. They also
-- give the front end a clean way to know whether this file has run at all: no
-- function, no controls.

-- Returns one json object rather than a row so the output names cannot
-- collide with the column names inside it. Null for a signed-out caller.
create or replace function public.privacy_settings()
returns json language sql security definer stable set search_path = public as $$
  select json_build_object(
           'share_progress', coalesce(p.share_progress, true),
           'share_activity', coalesce(p.share_activity, true),
           'hidden_slugs',   coalesce(p.hidden_slugs, '{}'::text[]))
    from (select auth.uid() as uid) me
    left join public.profiles p on p.user_id = me.uid
   where me.uid is not null;
$$;

-- Null means "leave that one alone", so the two switches never overwrite each
-- other — someone toggling activity on a phone cannot silently undo a
-- progress switch thrown on a laptop a second earlier.
create or replace function public.set_privacy(
  p_share boolean default null, p_activity boolean default null
) returns json language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then
    raise exception 'must be signed in to change privacy settings';
  end if;
  insert into public.profiles (user_id, share_progress, share_activity, updated_at)
  values (auth.uid(), coalesce(p_share, true), coalesce(p_activity, true), now())
  on conflict (user_id) do update
    set share_progress = coalesce(p_share, profiles.share_progress),
        share_activity = coalesce(p_activity, profiles.share_activity),
        updated_at     = now();
  return public.privacy_settings();
end $$;

-- One slug at a time, added and removed server-side, so two devices editing
-- the set cannot write each other's copy of the whole array back.
create or replace function public.set_list_hidden(p_slug text, p_hidden boolean)
returns json language plpgsql security definer set search_path = public as $$
declare cur text[];
begin
  if auth.uid() is null then
    raise exception 'must be signed in to change privacy settings';
  end if;
  -- the same shape src/build.py demands of a slug, so the column cannot fill
  -- up with anything that was never a list
  if p_slug is null or p_slug !~ '^[A-Za-z][A-Za-z0-9_-]*$' then
    raise exception 'that is not a list';
  end if;

  insert into public.profiles (user_id, updated_at) values (auth.uid(), now())
    on conflict (user_id) do nothing;
  select hidden_slugs into cur from public.profiles where user_id = auth.uid();

  if p_hidden then
    -- 500 is far past the whole catalogue and always will be at this rate; it
    -- is here so a scripted client cannot use somebody's profile row as free
    -- storage, not because anyone will ever hide a hundred lists.
    if coalesce(array_length(cur, 1), 0) >= 500 then
      raise exception 'too many hidden lists';
    end if;
    if not (p_slug = any (cur)) then cur := cur || p_slug; end if;
  else
    cur := array_remove(cur, p_slug);
  end if;

  update public.profiles set hidden_slugs = cur, updated_at = now()
   where user_id = auth.uid();
  return public.privacy_settings();
end $$;

-- Revoked from public, not only from anon: anon inherits execute through
-- PUBLIC, so revoking the role alone would leave the grant standing.
revoke all on function public.privacy_settings()             from public;
revoke all on function public.set_privacy(boolean, boolean)  from public;
revoke all on function public.set_list_hidden(text, boolean) from public;
grant execute on function public.privacy_settings()             to authenticated;
grant execute on function public.set_privacy(boolean, boolean)  to authenticated;
grant execute on function public.set_list_hidden(text, boolean) to authenticated;

-- ===========================================================================
-- PROVING IT BLOCKS — paste this into the SQL editor, it changes nothing
-- ===========================================================================
--
-- The claim worth checking by hand is that the DATABASE withholds the rows,
-- not that the page skips them. Impersonate the reader and ask for the row
-- directly; if RLS is doing the work, it comes back empty.
--
--   -- ids: A hides a list, B is A's mutual friend and wants to read it
--   -- select user_id, username from public.profiles;   (as postgres)
--
--   begin;
--     set local role authenticated;
--     set local request.jwt.claims = '{"sub":"<B-uuid>","role":"authenticated"}';
--     select property_id from public.progress where user_id = '<A-uuid>';
--   rollback;
--
-- Run it once before A hides anything: A's lists are listed. Have A hide one
-- (or run, as postgres:
--   update public.profiles set hidden_slugs = array['<slug>']
--    where user_id = '<A-uuid>';)
-- and run it again: that slug is gone from B's result, and so is `<slug>#fw`
-- if a fresh watch existed. Set share_progress false and B's result is empty
-- entirely. The row is still in the table — select it as postgres and it is
-- right there. B simply cannot reach it, which is the whole point.
--
-- The club branch, checked in the same breath: put A and B in a club for the
-- hidden list, then re-run the query as B. The row comes back, because
-- "read group progress" is a separate OR branch and this file never touched
-- it. If that row does NOT come back, something here has leaked into the club
-- path and must be undone before this ships.
