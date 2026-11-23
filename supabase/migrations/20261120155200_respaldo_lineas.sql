-- Copia de respaldo de las líneas del CAD (la app principal sigue en Firebase).
-- Solo escribe la función "respaldo" (con la llave de servicio, del lado del servidor); el público no tiene acceso.
create table public.respaldo_lineas (
  id text primary key,
  obra text not null default '',
  obra_id text not null default '',
  linea text not null default '',
  datos jsonb,
  borrada boolean not null default false,
  actualizado timestamptz not null,
  por_email text,
  por_nombre text,
  uid text,
  recibido timestamptz not null default now()
);
create index respaldo_lineas_obra_idx on public.respaldo_lineas (obra_id);

create table public.respaldo_versiones (
  n bigint generated always as identity primary key,
  linea_id text not null,
  obra text not null default '',
  linea text not null default '',
  datos jsonb,
  borrada boolean not null default false,
  actualizado timestamptz not null,
  por_email text,
  recibido timestamptz not null default now()
);
create index respaldo_versiones_linea_idx on public.respaldo_versiones (linea_id, n desc);

alter table public.respaldo_lineas enable row level security;
alter table public.respaldo_versiones enable row level security;
revoke all on public.respaldo_lineas, public.respaldo_versiones from anon, authenticated;

-- deja solo las últimas 30 versiones de cada línea
create function public.podar_versiones() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  delete from public.respaldo_versiones v
   where v.linea_id = new.linea_id
     and v.n not in (select n from public.respaldo_versiones where linea_id = new.linea_id order by n desc limit 30);
  return null;
end $$;
revoke execute on function public.podar_versiones() from public, anon, authenticated;
create trigger podar_versiones after insert on public.respaldo_versiones
  for each row execute function public.podar_versiones();

-- (segunda migración, respaldo_bom) listado de materiales (DP-F-009) calculado por la app para cada línea
alter table public.respaldo_lineas add column bom jsonb;

-- (tercera migración, respaldo_num_juntas) número de cada junta (W#) como sale en el plano
alter table public.respaldo_lineas add column num_juntas jsonb;
