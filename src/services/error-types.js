import { ErrorTypes } from '@/services/axios-client.js'

export const isClientError = errorType => {
  return [
    ErrorTypes.CLIENT_ERROR,
    ErrorTypes.UNAUTHORIZED,
    ErrorTypes.FORBIDDEN,
    ErrorTypes.NOTFOUND,
  ].includes(errorType)
}

export const isServerError = errorType => {
  return [ErrorTypes.UNKNOWN_ERROR, ErrorTypes.SERVER_ERROR].includes(errorType)
}

export const isConnectionError = errorType => {
  return [ErrorTypes.CONNECTION_ERROR].includes(errorType)
}

export const isUnknownError = errorType => {
  return [ErrorTypes.UNKNOWN_ERROR].includes(errorType)
}
