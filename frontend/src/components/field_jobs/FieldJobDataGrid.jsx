import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Icon } from '@mui/material';
import apiClient from '../../api/client.js';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import '../../App.css';

const STATUS_OPTIONS = ['Pending', 'In-Progress', 'Completed', 'Failed'];
const PRIORITY_OPTIONS = ['Low', 'Medium', 'Critical']

// PENDING = "Pending"
//     IN_PROGRESS = "In-Progress"
//     COMPLETED = "Completed"
//     FAILED = "Failed"

//local state variables for tracking table rows, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function FieldJobDataGrid({ onSuccess }) {
  const [field_jobs, setFieldJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState({
    title: '',
    priority: '',
    status: '',
    equipment_id: '',
    operator_id: '',
  });
  const [errorFieldJob, setErrorFieldJob] = useState(null);
  const [editingId, setEditingId] = useState(null); // null if creating new field_job, number if updating a row

    //defines our DataGrid columns and maps them to our backend API response data
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'title', headerName: 'Title', width: 160 },
    { field: 'priority', headerName: 'Priority', width: 140 },
    { field: 'status', headerName: 'Status', width: 140 },
    { field: 'equipment_id', headerName: 'Equipment ID', width: 130, type: 'number' },
    { field: 'operator_id', headerName: 'Operator ID', width: 130, type: 'number' },
    { field: 'actions', headerName: '', width: 110, disableColumnMenu: true,
      renderCell: (params) => (
        <>
          <IconButton onClick={() => handleStartEdit(params.row)}>
            <EditIcon>
            </EditIcon>
          </IconButton>
          <IconButton onClick={() => handleDelete(params.row.id)}>
            <DeleteIcon>
            </DeleteIcon>
          </IconButton>
        </>
        
      )
    },
  ];

    // id: int
    // title: str
    // priority: FieldJobPriority
    // status: FieldJobStatus
    // equipment_id: int
    // operator_id: int


  //pulls our field_job data from our backend
  async function fetchFieldJobs() {
    setLoading(true);
    try {
      let response;
      response = await apiClient.get('/field_jobs');
      setFieldJobs(response.data);
      setError(null); //make sure we clear any old errors
    } catch {
        setError('Could not load data.');
    } finally {
        setLoading(false);
    }
  }

  // fetchFieldJobs();
  useEffect(() => {
    fetchFieldJobs();
  }, []);

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev)=> ({ ...prev, [field]: event.target.value}));
  }

  //handles the actual creation of a new field_job record in the db
  const handleCreate = async() => {
    setErrorFieldJob(null);
    try {
      await apiClient.post('/field_jobs', {
        ...formValues,
      equipment_id: Number(formValues.equipment_id),
      operator_id: Number(formValues.operator_id),
      });
      setDialogOpen(false);
      setFormValues({title: '', priority: '', status: '', equipment_id: '', operator_id: ''});
      onSuccess(`FieldJob ${formValues.title} created.`);
      await fetchFieldJobs(); //see the table data refreshed with the new field_job
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFieldJob(msg);
    }
  }

  // prefill editing form with existing values, so user can just change what they want
  const handleStartEdit = (row) => {
    setEditingId(row.id);
    setFormValues({
      title: row.title || '',
      priority: row.priority || '',
      status: row.status || '',
      equipment_id: row.equipment_id ?? '',
      operator_id: row.operator_id ?? '',
    });
    setDialogOpen(true);
  }

  //handles updating an field_job record in the db
  const handleUpdate = async() => {
    setErrorFieldJob(null);
    try {
      await apiClient.patch(`/field_jobs/${editingId}`, {
        ...formValues,
        equipment_id: Number(formValues.equipment_id),
        operator_id: Number(formValues.operator_id),
      });
      setDialogOpen(false);
      setEditingId(null);
      setFormValues({title: '', priority: '', status: '', equipment_id: '', operator_id: ''});
      onSuccess(`FieldJob ${formValues.title} updated.`);
      await fetchFieldJobs(); //see the table data refreshed with the new field_job
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFieldJob(msg);
    }
  }

  //handles deletion of an field_job record in the db
  const handleDelete = async(id) => {
    setErrorFieldJob(null);
    const confirmed = window.confirm(`Delete field_job #${id}?`)
    if (!confirmed) return;

    try {
      await apiClient.delete(`/field_jobs/${id}`);
      onSuccess(`FieldJob #${id} deleted.`);
      await fetchFieldJobs(); //see the table data refreshed with the new field_job
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFieldJob(msg);
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Box id="field_job_btn_box">
        <Button id="add_field_job_btn" variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Field Job</Button>
      </Box>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={field_jobs} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle>{editingId ? `Edit FieldJob` : 'Add New FieldJob'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Title" value={formValues.title} onChange={handleFieldChange('title')} />
          <TextField select label="Priority" value={formValues.priority} onChange={handleFieldChange('priority')} >
            {PRIORITY_OPTIONS.map((option) => (
              <MenuItem key={option} value={option}>{option}</MenuItem>
            ))}
          </TextField>
          <TextField select label="Status" value={formValues.status} onChange={handleFieldChange('status')}>
            {STATUS_OPTIONS.map((option) => (
              <MenuItem key={option} value={option}>{option}</MenuItem>
            ))}
          </TextField>
          <TextField label="Equipment ID" type="number" value={formValues.equipment_id} onChange={handleFieldChange('equipment_id')} />
          <TextField label="Operator ID" type="number" value={formValues.operator_id} onChange={handleFieldChange('operator_id')} />
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                if (editingId !== null) {setFormValues({title: '', priority: '', status: '', equipment_id: '', operator_id: ''});};
                setDialogOpen(false)
              }}>Cancel</Button>
              <Button variant="contained" onClick={editingId ? handleUpdate : handleCreate}>
                {editingId ? 'Update' : 'Create'}
              </Button>
              {errorFieldJob && (<Alert severity="error">{errorFieldJob}</Alert>)}
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default FieldJobDataGrid; 