import model

class Solver:
    def __init__(self, model2Solve):
        if not isinstance(model2Solve, model.Model):
            raise TypeError("Expected an instance of model or its subclass.")
        self.__model__ = model2Solve

    def step(self, t, dt):
        """Should be implemented in derived classes."""
        raise NotImplementedError("This method should be implemented by subclasses.")

class SolverExplicit(Solver):
    def __init__(self, model2Solve):
        super().__init__(model2Solve)

    def step(self, t, dt):
        """Perform one step of numerical integration (e.g., explicit Euler)."""
        current_state = self.__model__.get_state()
        
        # Call the model's dydt method to get the derivatives of the state
        derivatives = self.__model__.dydt(t)
        
        # Update the state using the Euler method
        new_state = current_state + derivatives * dt
        self.__model__.set_state(new_state)

class SolverImplicit(Solver):
    def __init__(self, model2Solve):
        super().__init__(model2Solve)

    def step(self, t, dt):
        """Perform one step of implicit integration (e.g., implicit Euler)."""
        current_state = self.__model__.get_state()

        def implicit_function(new_state):
            """Implicit update function."""
            # Set the state in the model to new_state temporarily
            self.__model__.set_state(new_state)
            # Compute dydt at the new state and return the implicit function result
            return new_state - (current_state + self.__model__.dydt(t + dt) * dt)

        # Initial guess for the new state (using the current state)
        new_state_guess = current_state.copy()

        # Fixed-point iteration to solve for the new state
        for _ in range(10):
            new_state_guess = new_state_guess - 0.5 * implicit_function(new_state_guess)

        # Set the final guessed state in the model
        self.__model__.set_state(new_state_guess)