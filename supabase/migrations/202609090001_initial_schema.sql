create extension if not exists "pgcrypto";

create type public.resource_kind as enum ('practical', 'note', 'book', 'guideline', 'notebook', 'pdf', 'document');
create type public.processing_status as enum ('pending', 'processing', 'ready', 'failed');

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.subjects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 120),
  description text not null default '' check (char_length(description) <= 500),
  archived boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_id, name)
);

create table public.resources (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  subject_id uuid not null references public.subjects(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 200),
  description text not null default '' check (char_length(description) <= 2000),
  kind public.resource_kind not null,
  processing_status public.processing_status not null default 'pending',
  processing_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.files (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  resource_id uuid not null references public.resources(id) on delete cascade,
  storage_path text not null unique,
  filename text not null check (char_length(filename) between 1 and 255),
  content_type text not null check (char_length(content_type) between 1 and 255),
  size_bytes bigint not null check (size_bytes > 0 and size_bytes <= 104857600),
  created_at timestamptz not null default now()
);

create table public.tags (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 50),
  unique (owner_id, name)
);

create table public.resource_tags (
  resource_id uuid not null references public.resources(id) on delete cascade,
  tag_id uuid not null references public.tags(id) on delete cascade,
  primary key (resource_id, tag_id)
);

create index subjects_owner_id_idx on public.subjects(owner_id);
create index resources_owner_subject_idx on public.resources(owner_id, subject_id);
create index files_owner_resource_idx on public.files(owner_id, resource_id);
create index resource_tags_tag_id_idx on public.resource_tags(tag_id);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger subjects_updated_at before update on public.subjects
for each row execute function public.set_updated_at();
create trigger resources_updated_at before update on public.resources
for each row execute function public.set_updated_at();
create trigger profiles_updated_at before update on public.profiles
for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'name', new.email));
  return new;
end;
$$;

create trigger on_auth_user_created after insert on auth.users
for each row execute function public.handle_new_user();

alter table public.profiles enable row level security;
alter table public.subjects enable row level security;
alter table public.resources enable row level security;
alter table public.files enable row level security;
alter table public.tags enable row level security;
alter table public.resource_tags enable row level security;

create policy "users read own profile" on public.profiles for select using (auth.uid() = id);
create policy "users update own profile" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

create policy "users manage own subjects" on public.subjects for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "users manage own resources" on public.resources for all using (auth.uid() = owner_id) with check (
  auth.uid() = owner_id and exists (
    select 1 from public.subjects where subjects.id = subject_id and subjects.owner_id = auth.uid()
  )
);
create policy "users manage own files" on public.files for all using (auth.uid() = owner_id) with check (
  auth.uid() = owner_id and exists (
    select 1 from public.resources where resources.id = resource_id and resources.owner_id = auth.uid()
  )
);
create policy "users manage own tags" on public.tags for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "users manage own resource tags" on public.resource_tags for all using (
  exists (select 1 from public.resources where resources.id = resource_id and resources.owner_id = auth.uid())
  and exists (select 1 from public.tags where tags.id = tag_id and tags.owner_id = auth.uid())
) with check (
  exists (select 1 from public.resources where resources.id = resource_id and resources.owner_id = auth.uid())
  and exists (select 1 from public.tags where tags.id = tag_id and tags.owner_id = auth.uid())
);

insert into storage.buckets (id, name, public, file_size_limit)
values ('resource-files', 'resource-files', false, 104857600)
on conflict (id) do nothing;

create policy "users upload own resource files" on storage.objects for insert to authenticated
with check (bucket_id = 'resource-files' and (storage.foldername(name))[1] = (select auth.uid()::text));
create policy "users read own resource files" on storage.objects for select to authenticated
using (bucket_id = 'resource-files' and (storage.foldername(name))[1] = (select auth.uid()::text));
create policy "users delete own resource files" on storage.objects for delete to authenticated
using (bucket_id = 'resource-files' and (storage.foldername(name))[1] = (select auth.uid()::text));
