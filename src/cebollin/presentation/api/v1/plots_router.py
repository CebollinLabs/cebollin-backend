import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ....application.dto import PlotDTO, PlotCreateDTO, PlotUpdateDTO
from ....application.services import PlotService
from ...container import get_db, get_plot_service
from ...auth import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/plots", tags=["Plot Management"])


@router.post("/", response_model=PlotDTO, status_code=status.HTTP_201_CREATED)
def create_plot(
    plot_data: PlotCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PlotService = Depends(get_plot_service),
    db: Session = Depends(get_db),
):
    """Creates a new plot for the user's company."""
    try:
        plot = service.create_plot(plot_data, current_user)
        db.commit()
        return plot
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PlotDTO])
def list_plots(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PlotService = Depends(get_plot_service),
):
    """Lists all plots for the user's company."""
    return service.list_plots_for_company(current_user)


@router.put("/{plot_id}", response_model=PlotDTO)
def update_plot(
    plot_id: uuid.UUID,
    plot_data: PlotUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PlotService = Depends(get_plot_service),
    db: Session = Depends(get_db),
):
    """Updates a plot's name."""
    updated_plot = service.update_plot(plot_id, plot_data, current_user)
    if not updated_plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot not found or access denied.",
        )
    db.commit()
    return updated_plot


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plot(
    plot_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PlotService = Depends(get_plot_service),
    db: Session = Depends(get_db),
):
    """Deletes a plot."""
    success = service.delete_plot(plot_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot not found or access denied.",
        )
    db.commit()
    return None
