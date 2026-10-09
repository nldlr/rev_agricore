import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Typography  } from '@mui/material';
import apiClient from '../../api/client.js';

//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function ServiceReportDataGrid({ onSuccess }) {
  const [service_reports, setServiceReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [errorServiceReport, setErrorServiceReport] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [fieldJobId, setFieldJobId] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  //defines our DataGrid columns and maps them to our backend API response data
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'field_job_id', headerName: 'Field Job ID', width: 120, type: 'number' },
    { field: 'file_url', headerName: 'File Url', width: 360,
      renderCell: (params) => (
        <a href={params.value} target="_blank" rel="noopener noreferrer">
          {params.value}
        </a>
      )
    },
    { field: 'notes', headerName: 'Notes', width: 230 },
    { field: 'timestamp', headerName: 'Timestamp', width: 260 },
  ];

  //pulls our service_report data from our backend
  async function fetchServiceReports() {
    setLoading(true);
    try {
      const response = await apiClient.get('/service_reports');
      setServiceReports(response.data);
      setError(null); //make sure we clear any old errors
    } catch {
        setError('Could not load data.');
    } finally {
        setLoading(false);
    }
  }

  // fetchServiceReports();
  useEffect(() => {
    fetchServiceReports();
  }, []);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };


  //handles the actual creation of a new service_report record in the db
  const handleCreate = async() => {
    setErrorServiceReport(null);
    try {
      // await apiClient.post('/service_reports', {
      //   ...formValues,
      // field_job_id: Number(formValues.field_job_id),
      // });

      // New way to package payload because of file upload.
      const formData = new FormData();
      formData.append('field_job_id', fieldJobId);
      formData.append('notes', notes);
      formData.append('file', selectedFile); // file: UploadFile

      await apiClient.post('/service_reports', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDialogOpen(false);
      // setFormValues({field_job_id: '', file_url: '', notes: ''});
      setFieldJobId('');
      setNotes('');
      setSelectedFile(null);
      onSuccess(`Service report created.`);
      await fetchServiceReports(); //see the table data refreshed with the new service_report
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorServiceReport(msg);
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Button variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Service Report</Button>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={service_reports} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle sx={{color: 'black'}}>Add New Service Report</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Field Job ID" type="number" value={fieldJobId} onChange={(e) => setFieldJobId(e.target.value)} />
          <TextField label="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
          <Button
              component="label"
            >
              Upload File (TXT/PDF)
              <input
                type="file"
                hidden
                accept=".pdf,.txt,application/pdf,text/plain"
                onChange={handleFileChange}
              />
            </Button>
            {selectedFile && (
              <Typography >
                {" > "}{selectedFile.name}
              </Typography>
            )}
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button variant="contained" onClick={handleCreate}>Create</Button>
              {errorServiceReport && (<Alert severity="error">{errorServiceReport}</Alert>)}
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default ServiceReportDataGrid; 