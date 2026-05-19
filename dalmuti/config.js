// Supabase 프로젝트 설정.
//
// 멀티플레이어(친구 초대) 기능을 쓰려면 https://supabase.com 에서 무료 프로젝트를 만들고
// Project Settings → API 에서 URL 과 anon/public key 를 복사해 아래 값을 채워 넣으세요.
// 비워 두면 솔로(AI 봇 전용) 모드로 동작합니다.
//
// anon key 는 공개되어도 안전한 클라이언트용 키입니다. service_role key 는 절대 여기에 넣지 마세요.
export const SUPABASE_URL = "https://hbpllhgtlbzqzqwjwupj.supabase.co";
export const SUPABASE_ANON_KEY = "sb_publishable_jPe6Xuexv8qxtBDEMiadJQ_KZ_rHCsU";

export const APP_NAME = "Dalmuti";
export const ROOM_CODE_LENGTH = 6;
export const MIN_PLAYERS = 4;
export const MAX_PLAYERS = 8;
