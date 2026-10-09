import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Icon } from '@mui/material';
import apiClient from '../../api/client.js';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import RestoreIcon from '@mui/icons-material/Restore';
import '../../App.css';

//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function AuditDataGrid({ onSuccess }) {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState({
    user_id: '',
    action: '',
    entity_type: '',
    entity_id: '',
  });
  const [errorAudit, setErrorAudit] = useState(null);
  const [editingId, setEditingId] = useState(null); // null if creating new audit, number if updating a row

    //defines our DataGrid columns and maps them to our backend API response data
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'user_id', headerName: 'User ID', width: 100, type: 'number'},
    { field: 'action', headerName: 'Action', width: 160 },
    { field: 'entity_type', headerName: 'Entity Type', width: 160  },
    { field: 'entity_id', headerName: 'Entity ID', width: 100, type: 'number' },
    { field: 'actions', headerName: '', width: 110, disableColumnMenu: true,
      renderCell: (params) => (
        <>
          {/* <IconButton onClick={() => handleStartEdit(params.row)}>
            <EditIcon>
            </EditIcon>
          </IconButton> */}
          <IconButton onClick={() => handleRestore(params.row.id,params.row.entity_id)}>
            <RestoreIcon>
            </RestoreIcon>
          </IconButton>
        </>
        
      )
    },
  ];

// id | user_id | action | entity_type | entity_id

  //pulls our audit data from our backend
  async function fetchAudits() {
    setLoading(true);
    try {
      let response;
      response = await apiClient.get('/audits');
      setAudits(response.data);
      setError(null); //make sure we clear any old errors
    } catch {
        setError('Could not load data.');
    } finally {
        setLoading(false);
    }
  }

  // fetchAudits();
  useEffect(() => {
    fetchAudits();
  }, []);

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev)=> ({ ...prev, [field]: event.target.value}));
  }


  //handles the actual creation of a new audit record in the db
  const handleCreate = async() => {
    setErrorAudit(null);
    try {
      await apiClient.post('/audits', {
        ...formValues,
      entity_type: Number(formValues.entity_type),
      entity_id: Number(formValues.entity_id),
      });
      setDialogOpen(false);
      setFormValues({user_id: '', action: '', entity_type: '', entity_id: ''});
      onSuccess(`Audit ${formValues.user_id} created.`);
      await fetchAudits(); //see the table data refreshed with the new audit
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorAudit(msg);
    }
  }

  // prefill editing form with existing values, so user can just change what they want
  const handleStartEdit = (row) => {
    setEditingId(row.id);
    setFormValues({
      user_id: row.user_id || '',
      action: row.action || '',
      entity_type: row.entity_type ?? '',
      entity_id: row.entity_id ?? '',
    });
    setDialogOpen(true);
  }

  //handles updating an audit record in the db
  const handleUpdate = async() => {
    setErrorAudit(null);
    try {
      await apiClient.patch(`/audits/${editingId}`, {
        ...formValues,
        entity_type: Number(formValues.entity_type),
        entity_id: Number(formValues.entity_id),
      });
      setDialogOpen(false);
      setEditingId(null);
      setFormValues({user_id: '', action: '', entity_type: '', entity_id: ''});
      onSuccess(`Audit ${formValues.user_id} updated.`);
      await fetchAudits(); //see the table data refreshed with the new audit
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorAudit(msg);
    }
  }

  //handles deletion of an audit record in the db
  const handleRestore = async(id, entity_id) => {
    setErrorAudit(null);
    const confirmed = window.confirm(`Restore audit #${id}?`)
    if (!confirmed) return;

    try {
      await apiClient.patch(`/users/${entity_id}/restore`); // stretch goal, should be audits, but hardcoded to users
      onSuccess(`Audit #${id} restored.`);
      await fetchAudits(); //see the table data refreshed with the new audit
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorAudit(msg);
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Box id="audit_btn_box">
        {/* <Button id="add_audit_btn" variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Audit</Button> */}
      </Box>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={audits} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle sx={{color: 'black'}}>{editingId ? `Edit Audit` : 'Add New Audit'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Name" value={formValues.user_id} onChange={handleFieldChange('user_id')} />
          <TextField label="Location Region" value={formValues.action} onChange={handleFieldChange('action')} />
          <TextField label="Capacity" type="number" value={formValues.entity_type} onChange={handleFieldChange('entity_type')} />
          <TextField label="Supervisor Id" type="number" value={formValues.entity_id} onChange={handleFieldChange('entity_id')} />
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                if (editingId !== null) {setFormValues({user_id: '', action: '', entity_type: '', entity_id: ''});};
                setDialogOpen(false)
              }}>Cancel</Button>
              <Button variant="contained" onClick={editingId ? handleUpdate : handleCreate}>
                {editingId ? 'Update' : 'Create'}
              </Button>
              {errorAudit && (<Alert severity="error">{errorAudit}</Alert>)}
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default AuditDataGrid; 