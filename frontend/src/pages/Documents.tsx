import React, { useEffect, useRef, useState } from 'react'
import { Container, Table, Button, Form, ProgressBar } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorAlert } from '@/components/ErrorAlert'
import { documentApi } from '@/api/documents'
import { Document } from '@/types'
import { useNotification } from '@/hooks/useNotification'

export const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { success, error: errorNotification } = useNotification()

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const docs = await documentApi.list()
      setDocuments(docs)
    } catch (err) {
      setError('Failed to load documents')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.includes('pdf')) {
      errorNotification('Please select a PDF file')
      return
    }

    setUploading(true)
    setUploadProgress(0)

    try {
      const result = await documentApi.upload(file)
      setUploadProgress(100)
      success(`Document uploaded: ${result.filename}`)
      await fetchDocuments()
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      errorNotification('Failed to upload document')
      console.error(err)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDelete = async (filename: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return

    try {
      await documentApi.delete(filename)
      success('Document deleted')
      await fetchDocuments()
    } catch (err) {
      errorNotification('Failed to delete document')
      console.error(err)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <Layout>
      <Container fluid>
        <h1 className="mb-4">
          <i className="bi bi-file-earmark-pdf me-2"></i>
          Documents
        </h1>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        <div className="card mb-4">
          <div className="card-header">
            <h6 className="mb-0">Upload Document</h6>
          </div>
          <div className="card-body">
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
                  Upload PDF documents for policy analysis and semantic search
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
                {uploading ? 'Uploading...' : 'Select File'}
              </Button>
            </Form>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Uploaded Documents</h6>
          </div>
          <div className="card-body">
            {documents.length > 0 ? (
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Size</th>
                    <th>Chunks</th>
                    <th>Indexed At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.filename}>
                      <td>
                        <i className="bi bi-file-earmark-pdf me-2"></i>
                        {doc.filename}
                      </td>
                      <td>{(doc.size / 1024).toFixed(2)} KB</td>
                      <td>{doc.chunks}</td>
                      <td className="text-muted small">
                        {new Date(doc.indexed_at).toLocaleDateString()}
                      </td>
                      <td>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(doc.filename)}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <p className="text-muted">No documents uploaded yet</p>
            )}
          </div>
        </div>
      </Container>
    </Layout>
  )
}
