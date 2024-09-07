/*
    * This file contains the enum defining the possible states of the
    * flashcard generation task in the backend. The values of the
    * enum are used by the API and backend, and should not be changed.
 */
export enum TaskState {
    pending = 'PENDING',
    started = 'STARTED',
    inProgress =  'IN_PROGRESS',
    success = 'SUCCESS',
    failure = 'FAILURE',
    retry = 'RETRY',
    revoked = 'REVOKED',
}