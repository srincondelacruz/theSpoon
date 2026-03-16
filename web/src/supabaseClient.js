import { createClient } from '@supabase/supabase-js';

// Ensure it's a valid URL format even if placeholder, to prevent crash on mount
const envUrl = import.meta.env.VITE_SUPABASE_URL;
export const supabaseUrl = (envUrl && envUrl.startsWith('http')) ? envUrl : 'https://placeholder.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-key';

export const supabase = createClient(supabaseUrl, supabaseKey);
