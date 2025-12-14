import apiClient from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:19',message:'LOGIN_START',data:{email:data.email,passwordLength:data.password?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    // FastAPI OAuth2PasswordRequestForm expects form data with 'username' field
    const formData = new FormData()
    formData.append('username', data.email)  // OAuth2 uses 'username' field
    formData.append('password', data.password)
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:25',message:'LOGIN_REQUEST_DETAILS',data:{url:'/api/v1/auth/login',formDataUsername:data.email,hasPassword:!!data.password},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    
    try {
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:33',message:'LOGIN_SUCCESS',data:{status:response.status,hasToken:!!response.data?.access_token,tokenType:response.data?.token_type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      return response.data
    } catch (error: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:38',message:'LOGIN_ERROR',data:{hasResponse:!!error.response,status:error.response?.status,statusText:error.response?.statusText,detail:error.response?.data?.detail,message:error.message,code:error.code},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      throw error
    }
  },

  register: async (data: RegisterRequest) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:44',message:'REGISTER_START',data:{email:data.email,passwordLength:data.password?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    try {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:47',message:'REGISTER_REQUEST_DETAILS',data:{url:'/api/v1/auth/register',email:data.email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      const response = await apiClient.post('/auth/register', data)
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:50',message:'REGISTER_SUCCESS',data:{status:response.status,userId:response.data?.id,email:response.data?.email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      return response.data
    } catch (error: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'auth.ts:53',message:'REGISTER_ERROR',data:{hasResponse:!!error.response,status:error.response?.status,statusText:error.response?.statusText,detail:error.response?.data?.detail,message:error.message,code:error.code,isNetworkError:!error.response},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      // Log the full error for debugging
      console.error('Registration API error:', error)
      if (!error.response) {
        throw new Error('Unable to connect to server. Please ensure the backend is running on http://localhost:8000')
      }
      throw error
    }
  },
}

