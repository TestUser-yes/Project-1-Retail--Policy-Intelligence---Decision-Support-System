import React, { useRef, useState } from 'react'
import { Container, Button, Form, ProgressBar, Alert } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { ErrorAlert } from '@/components/ErrorAlert'
import { documentApi } from '@/api/documents'
import { useNotification } from '@/hooks/useNotification'

export const Documents: React.FC = () => {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ filename: string; chunks: number; timestamp: string }>>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { addNotification } = useNotification()

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.includes('pdf')) {
      addNotification('Please select a PDF file', 'error')
      return
    }

    setUploading(true)
    setUploadProgress(0)
    setError('')

    try {
      const result = await documentApi.upload(file)
      setUploadProgress(100)
      addNotification(
        `Document uploaded: ${result.filename} (${result.chunks_created} chunks)`,
        'success'
      )

      setUploadedFiles(prev => [...prev, {
        filename: result.filename,
        chunks: result.chunks_created,
        timestamp: result.timestamp
      }])

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to upload document'
      setError(errorMsg)
      addNotification(errorMsg, 'error')
      console.error(err)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  return (
    <Layout>
      <Container fluid>
        <h1 className="mb-4">
          <i className="bi bi-file-earmark-pdf me-2"></i>
          Policy Documents
        </h1>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        <div className="card mb-4">
          <div className="card-header">
            <h6 className="mb-0">Upload Policy Document</h6>
          </div>
          <div className="card-body">
            <p className="text-muted mb-3">
              Upload PDF documents containing policy information. These will be indexed and made searchable for the Policy Assistant.
            </p>
            <Form>
              <Form.Group>
                <Form.Label>Select PDF File</Form.Label>
                <Form.Control
                  type="file"
                  accept=".pdf"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  disabled={uploading}
                />
                <Form.Text className="d-block text-muted mt-2">
                  Supported format: PDF | Maximum recommended size: 50MB
                </Form.Text>
              </Form.Group>

              {uploadProgress > 0 && (
                <div className="mt-3">
                  <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} />
                </div>
              )}

              <Button
                variant="primary"
                type="button"
                disabled={uploading}
                className="mt-3"
                onClick={() => fileInputRef.current?.click()}
              >
                {uploading ? 'Uploading...' : 'Select PDF File'}
              </Button>
            </Form>
          </div>
        </div>

        {uploadedFiles.length > 0 && (
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Recent Uploads ({uploadedFiles.length})</h6>
            </div>
            <div className="card-body">
              <div className="list-group">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="list-group-item">
                    <div className="d-flex w-100 justify-content-between align-items-start">
                      <div>
                        <div className="mb-2">
                          <i className="bi bi-file-earmark-pdf me-2 text-danger"></i>
                          <strong>{file.filename}</strong>
                        </div>
                        <small className="text-muted">
                          {file.chunks} chunks • {new Date(file.timestamp).toLocaleString()}
                        </small>
                      </div>
                      <span className="badge bg-success">Indexed</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {uploadedFiles.length === 0 && !error && (
          <Alert variant="info">
            <i className="bi bi-info-circle me-2"></i>
            No documents uploaded yet. Upload a PDF file to get started with the Policy Assistant.
          </Alert>
        )}
      </Container>
    </Layout>
  )
}
