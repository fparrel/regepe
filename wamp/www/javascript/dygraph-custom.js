/*
Dygraph.Interaction.startSelection = function(event, g, context) {
  context.isSelecting = true;
  context.selectionMoved = false;
};

Dygraph.Interaction.moveSelection = function(event, g, context) {
  context.selectionMoved = true;
  context.dragEndX = Dygraph.dragGetX_(event, context);
  context.dragEndY = Dygraph.dragGetY_(event, context);

  var xDelta = Math.abs(context.dragStartX - context.dragEndX);
  var yDelta = Math.abs(context.dragStartY - context.dragEndY);

  // drag direction threshold for y axis is twice as large as x axis
  context.dragDirection = (xDelta < yDelta / 2) ? Dygraph.VERTICAL : Dygraph.HORIZONTAL;

  g.drawZoomRect_(
      context.dragDirection,
      context.dragStartX,
      context.dragEndX,
      context.dragStartY,
      context.dragEndY,
      context.prevDragDirection,
      context.prevEndX,
      context.prevEndY);

  context.prevEndX = context.dragEndX;
  context.prevEndY = context.dragEndY;
  context.prevDragDirection = context.dragDirection;
};

Dygraph.Interaction.endSelection = function(event, g, context) {
    context.isSelecting = false;
  context.dragEndX = Dygraph.dragGetX_(event, context);
  context.dragEndY = Dygraph.dragGetY_(event, context);
  var regionWidth = Math.abs(context.dragEndX - context.dragStartX);
  var regionHeight = Math.abs(context.dragEndY - context.dragStartY);
};

Dygraph.startSelection = Dygraph.Interaction.startSelection;
Dygraph.moveSelection = Dygraph.Interaction.moveSelection;
Dygraph.endSelection = Dygraph.Interaction.endSelection;
*/

var MyDygraphInteractionModel = {
  // Track the beginning of drag events
  mousedown: function(event, g, context) {
    // Right-click should not initiate a zoom.
    if (event.button && event.button == 2) return;

    context.initializeMouseDown(event, g, context);

    if (event.altKey) {
        Dygraph.startPan(event, g, context);
    } else if (event.shiftKey) {
        Dygraph.startSelection(event, g, context);
    } else {
        Dygraph.startZoom(event, g, context);
    }
  },

  // Draw zoom rectangles when the mouse is down and the user moves around
  mousemove: function(event, g, context) {
    if (context.isZooming) {
      Dygraph.moveZoom(event, g, context);
    } else if (context.isPanning) {
      Dygraph.movePan(event, g, context);
    } else if (context.isSelecting) {
      Dygraph.moveSelection(event, g, context);
    }
  },

  mouseup: function(event, g, context) {
    if (context.isZooming) {
      Dygraph.endZoom(event, g, context);
    } else if (context.isPanning) {
      Dygraph.endPan(event, g, context);
    }else if (context.isSelecting) {
      Dygraph.endSelection(event, g, context);
       onGraphSelectionChanged(g.findClosestRow(g.currentSelection[1]),g.findClosestRow(g.currentSelection[2]));
    }
  },

  touchstart: function(event, g, context) {
    Dygraph.Interaction.startTouch(event, g, context);
  },
  touchmove: function(event, g, context) {
    Dygraph.Interaction.moveTouch(event, g, context);
  },
  touchend: function(event, g, context) {
    Dygraph.Interaction.endTouch(event, g, context);
  },

  // Temporarily cancel the dragging event when the mouse leaves the graph
  mouseout: function(event, g, context) {
    if (context.isZooming) {
      context.dragEndX = null;
      context.dragEndY = null;
      g.clearZoomRect_();
    }
  },

  // Disable zooming out if panning.
  dblclick: function(event, g, context) {
    if (context.cancelNextDblclick) {
      context.cancelNextDblclick = false;
      return;
    }
    if (event.altKey || event.shiftKey) {
      return;
    }
    g.resetZoom();
  }
};


