import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Icon } from '@mui/material';
import apiClient from '../../api/client.js';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import '../../App.css';

const STATUS_OPTIONS = ['Idle', 'In-Use', 'Maintenance', 'Retired'];

//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function EquipmentDataGrid({ onSuccess }) {
  const [equipments, setEquipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState({
    serial_number: '',
    model: '',
    fuel_level: '',
    farm_id: '',
    status: 'Idle',
  });
  const [lowFuelFlag, setLowFuelFlag] = useState(false);
  const [errorEquipment, setErrorEquipment] = useState(null);
  const [editingId, setEditingId] = useState(null); // null if creating new equipment, number if updating a row

    //defines our DataGrid columns and maps them to our backend API response data
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'serial_number', headerName: 'Serial Number', width: 150 },
    { field: 'model', headerName: 'Model', width: 160 },
    { field: 'fuel_level', headerName: 'Fuel %', width: 120, type: 'number' },
    { field: 'status', headerName: 'Status', width: 130 },
    { field: 'farm_id', headerName: 'Farm ID', width: 110, type: 'number' },
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


  //pulls our equipment data from our backend
  async function fetchEquipments() {
    setLoading(true);
    try {
      let response;
      if (lowFuelFlag) {
        response = await apiClient.get('/equipments', {
          params: { max_fuel: 20.0 },
        });
      } else {
        response = await apiClient.get('/equipments');
      }
      setEquipments(response.data);
      setError(null); //make sure we clear any old errors
    } catch {
        setError('Could not load data.');
    } finally {
        setLoading(false);
    }
  }

  // fetchEquipments();
  useEffect(() => {
    fetchEquipments();
  }, []);

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev)=> ({ ...prev, [field]: event.target.value}));
  }

  const handleFuelToggle = async() => {
    setLowFuelFlag((prev) => !prev);
  }
  const equipmentRowsFilter = lowFuelFlag ? equipments.filter((item) => item.fuel_level <= 20) : equipments

  //handles the actual creation of a new equipment record in the db
  const handleCreate = async() => {
    setErrorEquipment(null);
    try {
      await apiClient.post('/equipments', {
        ...formValues,
      fuel_level: Number(formValues.fuel_level),
      farm_id: Number(formValues.farm_id),
      });
      setDialogOpen(false);
      setFormValues({serial_number: '', model: '', fuel_level: '', farm_id: '', status: 'Idle'});
      onSuccess(`Equipment ${formValues.serial_number} created.`);
      await fetchEquipments(); //see the table data refreshed with the new equipment
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorEquipment(msg);
    }
  }

  // prefill editing form with existing values, so user can just change what they want
  const handleStartEdit = (row) => {
    setEditingId(row.id);
    setFormValues({
      serial_number: row.serial_number || '',
      model: row.model || '',
      fuel_level: row.fuel_level ?? '',
      farm_id: row.farm_id ?? '',
      status: row.status || 'Idle',
    });
    setDialogOpen(true);
  }

  //handles updating an equipment record in the db
  const handleUpdate = async() => {
    setErrorEquipment(null);
    try {
      await apiClient.patch(`/equipments/${editingId}`, {
        ...formValues,
        fuel_level: Number(formValues.fuel_level),
        farm_id: Number(formValues.farm_id),
      });
      setDialogOpen(false);
      setEditingId(null);
      setFormValues({serial_number: '', model: '', fuel_level: '', farm_id: '', status: 'Idle'});
      onSuccess(`Equipment ${formValues.serial_number} updated.`);
      await fetchEquipments(); //see the table data refreshed with the new equipment
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorEquipment(msg);
    }
  }

  //handles deletion of an equipment record in the db
  const handleDelete = async(id) => {
    setErrorEquipment(null);
    const confirmed = window.confirm(`Delete equipment #${id}?`)
    if (!confirmed) return;

    try {
      await apiClient.delete(`/equipments/${id}`);
      onSuccess(`Equipment #${id} deleted.`);
      await fetchEquipments(); //see the table data refreshed with the new equipment
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorEquipment(msg);
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Box id="equipment_btn_box">
        <Button id="add_equipment_btn" variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Equipment</Button>
        <Button id="filter_equipment_btn" onClick={handleFuelToggle}>Low Fuel Filter: {lowFuelFlag ? "ON (<20%)" : "OFF"}</Button>
      </Box>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={equipmentRowsFilter} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle sx={{ 
        color: 'black' 
      }}>{editingId ? `Edit Equipment` : 'Add New Equipment'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Serial Number" value={formValues.serial_number} onChange={handleFieldChange('serial_number')} />
          <TextField label="Model" value={formValues.model} onChange={handleFieldChange('model')} />
          <TextField label="Fuel Level" type="number" value={formValues.fuel_level} onChange={handleFieldChange('fuel_level')} />
          <TextField label="Farm ID" type="number" value={formValues.farm_id} onChange={handleFieldChange('farm_id')} />
          <TextField select label="Status" value={formValues.status} onChange={handleFieldChange('status')}>
            {STATUS_OPTIONS.map((option) => (
              <MenuItem key={option} value={option}>{option}</MenuItem>
            ))}
          </TextField>
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                if (editingId !== null) {setFormValues({serial_number: '', model: '', fuel_level: '', farm_id: '', status: 'Idle'});};
                setDialogOpen(false)
              }}>Cancel</Button>
              <Button variant="contained" onClick={editingId ? handleUpdate : handleCreate}>
                {editingId ? 'Update' : 'Create'}
              </Button>
              {errorEquipment && (<Alert severity="error">{errorEquipment}</Alert>)}
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default EquipmentDataGrid; 